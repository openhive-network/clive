from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator, cast

from beekeepy import AsyncBeekeeper, AsyncSession, AsyncUnlockedWallet
from beekeepy import Settings as BeekeepySettings
from helpy import HttpUrl
from textual.reactive import var
from typing_extensions import override

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.commands.exceptions import NoProfileUnlockedError
from clive.__private.core.commands.get_unlocked_wallet import GetUnlockedWallet
from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.unlock import Unlock
from clive.exceptions import ProfileNotLoadedError

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount


class World:
    """
    World is a top-level container for all application objects.

    It is a single source of truth for interacting with the Clive application.

    Args:
    ----
    beekeepy_settings_or_url:  In case of passing url it will be set to settings.http_endpoint.
        Missing required fields will be automatically filled.
        If not provided all is set to defaults.

    Note:
    ----
    Depending on settings.http_endpoint, remote beekeeper will be used.
    If not set, local beekeeper will start with locked session.
    """

    def __init__(
        self,
        *args: Any,
        beekeepy_settings_or_url: BeekeepySettings | HttpUrl | None = None,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._profile: Profile | None = None
        self._known_exchanges = KnownExchanges()
        self._app_state = AppState(self)
        self._commands = self._setup_commands()
        self._beekeeper_settings = self._setup_beekeepy_settings(beekeepy_settings_or_url)
        self._beekeeper: AsyncBeekeeper | None = None
        self._session: AsyncSession | None = None
        self._unlocked_wallet: AsyncUnlockedWallet | None = None

        self._node: Node | None = None
        self._is_during_setup = False

    async def __aenter__(self) -> Self:
        return await self.setup()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    @property
    def profile(self) -> Profile:
        if self._profile is None:
            raise ProfileNotLoadedError
        return self._profile

    @property
    def node(self) -> Node:
        """Node shouldn't be used for direct API calls in CLI/TUI. Instead, use commands which also handle errors."""
        assert self._node is not None, "Node is not initialized"
        return self._node

    @property
    def app_state(self) -> AppState:
        return self._app_state

    @property
    def commands(self) -> Commands[World]:
        return self._commands

    @property
    def known_exchanges(self) -> KnownExchanges:
        return self._known_exchanges

    @property
    def _beekeeper_ensure(self) -> AsyncBeekeeper:
        assert self._beekeeper is not None, "Beekeeper is not initialized"
        return self._beekeeper

    @property
    def _session_ensure(self) -> AsyncSession:
        assert self._session is not None, "Session is not initialized"
        return self._session

    @property
    def _is_unlocked_wallet_set(self) -> bool:
        return self._unlocked_wallet is not None

    @property
    def _unlocked_wallet_ensure(self) -> AsyncUnlockedWallet:
        assert self._unlocked_wallet is not None, "Wallet is not initialized"
        return self._unlocked_wallet

    async def _set_unlocked_wallet(self, new_wallet: AsyncUnlockedWallet) -> None:
        assert new_wallet.name in [
            w.name for w in (await self._session_ensure.wallets)
        ], "This wallet does not exists within this session"
        self._unlocked_wallet = new_wallet

    @property
    def _should_sync_with_beekeeper(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    @asynccontextmanager
    async def during_setup(self) -> AsyncGenerator[None]:
        self._is_during_setup = True
        try:
            yield
        except Exception:
            await self.close()
            raise
        finally:
            self._is_during_setup = False

    async def setup(self) -> Self:
        async with self.during_setup():
            self._beekeeper = await self._setup_beekeeper()
            self._session = await self._beekeeper_ensure.session
        return self

    async def close(self) -> None:
        if self._profile is not None:
            self._profile.save()
        if self._node is not None:
            self._node.teardown()
        if self._beekeeper is not None:
            self._beekeeper.teardown()

    async def create_new_profile(
        self,
        name: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
    ) -> None:
        profile = Profile.create(name, working_account, watched_accounts)
        await self.switch_profile(profile)

    async def create_new_profile_with_beekeeper_wallet(
        self,
        name: str,
        password: str | None = None,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
    ) -> str:
        """
        Create a new profile and a. wallet in beekeeper in one-go.

        Since beekeeper wallet will be created, profile will be also saved.
        If beekeeper wallet creation fails, profile will not be saved.
        """
        await self.create_new_profile(name, working_account, watched_accounts)
        self.profile.save()

        create_wallet_wrapper = await self.commands.create_wallet(password=password)
        if create_wallet_wrapper.error_occurred:
            self.profile.delete()

        generated_password = create_wallet_wrapper.result_or_raise
        actual_password = password or generated_password
        assert actual_password is not None, "Looks like there's an issue with beekeeper password generation"
        return actual_password

    async def load_profile_based_on_beekepeer(self) -> None:
        unlocked_wallet = await self._get_unlocked_wallet(self._session_ensure)
        await self._set_unlocked_wallet(unlocked_wallet)

        profile = Profile.load(self._unlocked_wallet_ensure.name)
        await self.switch_profile(profile)
        if self._should_sync_with_beekeeper:
            await self._commands.sync_state_with_beekeeper()

    async def load_profile(self, profile_name: str) -> None:
        profile = Profile.load(profile_name)
        await self.switch_profile(profile)

    async def switch_profile(self, new_profile: Profile) -> None:
        self._profile = new_profile
        await self._update_node()

    def is_profile_available(self) -> bool:
        return self.profile is not None

    def on_going_into_locked_mode(self, source: LockSource) -> None:
        """Triggered when the application is going into the locked mode."""
        if self._is_during_setup:
            return
        self._on_going_into_locked_mode(source)

    def on_going_into_unlocked_mode(self) -> None:
        """Triggered when the application is going into the unlocked mode."""
        if self._is_during_setup:
            return
        self._on_going_into_unlocked_mode()

    async def _get_unlocked_wallet(self, session: AsyncSession) -> AsyncUnlockedWallet:
        return await GetUnlockedWallet(session=session).execute_with_result()

    def _on_going_into_locked_mode(self, _: LockSource) -> None:
        """Override this method to hook when clive goes into the locked mode."""

    def _on_going_into_unlocked_mode(self) -> None:
        """Override this method to hook when clive goes into the unlocked mode."""

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    async def _setup_beekeeper(self) -> AsyncBeekeeper:
        if self._beekeeper_settings.http_endpoint is not None:
            return await AsyncBeekeeper.remote_factory(url_or_settings=self._beekeeper_settings)

        return await AsyncBeekeeper.factory(settings=self._beekeeper_settings)

    async def _update_node(self) -> None:
        if self._profile is None:
            self._node = None
            return
        if self._node is None:
            self._node = Node(self._profile)
        else:
            self._node.change_related_profile(self._profile)

    @classmethod
    def _setup_beekeepy_settings(cls, beekeepy_settings_or_url: BeekeepySettings | HttpUrl | None) -> BeekeepySettings:
        if isinstance(beekeepy_settings_or_url, BeekeepySettings):
            settings = beekeepy_settings_or_url
        elif isinstance(beekeepy_settings_or_url, HttpUrl):
            settings = BeekeepySettings(http_endpoint=beekeepy_settings_or_url)
        else:
            settings = BeekeepySettings()

        return safe_settings.beekeeper.settings_factory(settings)


class TUIWorld(World, CliveDOMNode):
    profile: Profile = var(None, init=False)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    @override
    def __init__(self) -> None:
        super().__init__()
        self.app_state = self._app_state

    @property
    def commands(self) -> TUICommands:
        return cast(TUICommands, super().commands)

    @property
    def is_in_create_profile_mode(self) -> bool:
        return self.profile.name == WELCOME_PROFILE_NAME

    @property
    def _should_sync_with_beekeeper(self) -> bool:
        return super()._should_sync_with_beekeeper and not self.is_in_create_profile_mode

    @override
    async def setup(self) -> Self:
        """
        In TUIWorld we assume that profile (and node) is always loaded when entering context manager.

        It's initialized with None because reactive attribute initialization can't be delayed otherwise.
        """
        await super().setup()
        try:
            await self.load_profile_based_on_beekepeer()
        except NoProfileUnlockedError:
            await self._switch_to_welcome_profile()
        return self

    async def create_new_profile(
        self,
        name: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
    ) -> None:
        await super().create_new_profile(name, working_account, watched_accounts)
        self._update_profile_related_reactive_attributes()

    async def load_profile_based_on_beekepeer(self) -> None:
        await super().load_profile_based_on_beekepeer()
        self._update_profile_related_reactive_attributes()

    async def load_profile(self, profile_name: str) -> None:
        await super().load_profile(profile_name)
        self._update_profile_related_reactive_attributes()

    async def _switch_to_welcome_profile(self) -> None:
        """Set the profile to default (welcome)."""
        await self.create_new_profile(WELCOME_PROFILE_NAME)
        self.profile.skip_saving()

    def _watch_profile(self, profile: Profile) -> None:
        self.node.change_related_profile(profile)

    def _on_going_into_locked_mode(self, source: LockSource) -> None:
        if source == "beekeeper_monitoring_thread":
            self.app.notify("Switched to the LOCKED mode due to timeout.", timeout=10)
        self.profile.save()
        self.app.pause_refresh_node_data_interval()
        self.app.pause_refresh_alarms_data_interval()
        self.node.cached.clear()

        async def lock() -> None:
            self._add_welcome_modes()
            await self.app.switch_mode("unlock")
            await self._restart_dashboard_mode()
            await self._switch_to_welcome_profile()

        self.app.run_worker(lock())

    def _on_going_into_unlocked_mode(self) -> None:
        self.app.trigger_app_state_watchers()

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)

    def _add_welcome_modes(self) -> None:
        self.app.add_mode("create_profile", CreateProfileForm)
        self.app.add_mode("unlock", Unlock)

    async def _restart_dashboard_mode(self) -> None:
        await self.app.remove_mode("dashboard")
        self.app.add_mode("dashboard", Dashboard)

    def _update_profile_related_reactive_attributes(self) -> None:
        if self._node is not None:
            self.node = self._node
        if self._profile is not None:
            self.profile = self._profile


class CLIWorld(World):
    @property
    def commands(self) -> CLICommands:
        return cast(CLICommands, super().commands)

    @override
    async def setup(self) -> Self:
        await super().setup()
        try:
            await self.load_profile_based_on_beekepeer()
        except NoProfileUnlockedError as error:
            raise CLINoProfileUnlockedError from error
        return self

    def _setup_commands(self) -> CLICommands:
        return CLICommands(self)
