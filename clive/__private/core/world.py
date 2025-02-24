from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator, cast

from beekeepy import AsyncBeekeeper, AsyncSession
from beekeepy import Settings as BeekeepySettings
from textual.reactive import var
from typing_extensions import override

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.commands.get_unlocked_user_wallet import NoProfileUnlockedError
from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.core.wallet_manager import WalletManager
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
    """

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._profile: Profile | None = None
        self._known_exchanges = KnownExchanges()
        self._app_state = AppState(self)
        self._commands = self._setup_commands()
        self._beekeeper_settings = self._setup_beekeepy_settings()
        self._beekeeper: AsyncBeekeeper | None = None
        self._session: AsyncSession | None = None
        self._wallets: WalletManager | None = None

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
    def is_profile_available(self) -> bool:
        return self._profile is not None

    @property
    def node(self) -> Node:
        """Node shouldn't be used for direct API calls in CLI/TUI. Instead, use commands which also handle errors."""
        message = "Node is not available. It requires profile to be loaded. Is the profile available?"
        assert self._node is not None, message
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
    def wallets(self) -> WalletManager:
        message = "Wallets are not available. Did you forget to use as a context manager or call `setup`?"
        assert self._wallets is not None, message
        return self._wallets

    @property
    def beekeeper(self) -> AsyncBeekeeper:
        """
        Beekeeper shouldn't be used for API calls in CLI/TUI. Instead, use commands which also handle errors.

        Same applies for other beekeepy objects like session or wallet.
        """
        message = "Beekeeper is not available. Did you forget to use as a context manager or call `setup`?"
        assert self._beekeeper is not None, message
        return self._beekeeper

    @property
    def beekeeper_settings(self) -> BeekeepySettings:
        """Should be used only for modifying beekeeper settings before setup is done."""
        use_instead_for_modify = "world.beekeeper.update_settings"
        use_instead_for_read = "world.beekeeper.settings"
        message = (
            f"Usage impossible after setup, use `{use_instead_for_modify}` to modify "
            f"or `{use_instead_for_read}` for read instead."
        )
        assert self._beekeeper is None, message
        return self._beekeeper_settings

    @property
    def _session_ensure(self) -> AsyncSession:
        message = "Session is not available. Did you forget to use as a context manager or call `setup`?"
        assert self._session is not None, message
        return self._session

    @property
    def _should_sync_with_beekeeper(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    @property
    def _should_save_profile_on_close(self) -> bool:
        return self._profile is not None

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
            self._session = await self.beekeeper.session
            self._wallets = WalletManager(self._session)
        return self

    async def close(self) -> None:
        if self._should_save_profile_on_close:
            await self.commands.save_profile()
        if self._node is not None:
            self._node.teardown()
        if self._beekeeper is not None:
            self._beekeeper.teardown()

        self._beekeeper = None
        self._session = None
        self._wallets = None

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
        password: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
    ) -> None:
        """
        Create a new profile and wallets in beekeeper in one-go.

        Since beekeeper wallet will be created, profile will be also saved.
        If beekeeper wallet creation fails, profile will not be saved.
        """
        await self.create_new_profile(name, working_account, watched_accounts)

        create_wallet_wrapper = await self.commands.create_profile_wallets(password=password)
        result = create_wallet_wrapper.result_or_raise
        if create_wallet_wrapper.error_occurred:
            self.profile.delete()
        await self.wallets.set_wallets(WalletContainer(result.unlocked_user_wallet, result.unlocked_encryption_wallet))
        await self.commands.save_profile()

    async def load_profile_based_on_beekepeer(self) -> None:
        unlocked_user_wallet = (await self.commands.get_unlocked_user_wallet()).result_or_raise
        unlocked_encryption_wallet = (await self.commands.get_unlocked_encryption_wallet()).result_or_raise
        await self.wallets.set_wallets(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))

        profile_name = self.wallets.name
        profile = (await self.commands.load_profile(profile_name=profile_name)).result_or_raise
        await self.switch_profile(profile)
        if self._should_sync_with_beekeeper:
            await self.commands.sync_state_with_beekeeper()

    async def load_profile(self, profile_name: str, password: str) -> None:
        assert not self.app_state.is_unlocked, "Application is already unlocked"
        await self.commands.unlock(profile_name=profile_name, password=password, permanent=True)
        await self.load_profile_based_on_beekepeer()

    async def switch_profile(self, new_profile: Profile) -> None:
        self._profile = new_profile
        await self._update_node()

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

    def _on_going_into_locked_mode(self, _: LockSource) -> None:
        """Override this method to hook when clive goes into the locked mode."""

    def _on_going_into_unlocked_mode(self) -> None:
        """Override this method to hook when clive goes into the unlocked mode."""

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    async def _setup_beekeeper(self) -> AsyncBeekeeper:
        if self.beekeeper_settings.http_endpoint is not None:
            return await AsyncBeekeeper.remote_factory(url_or_settings=self.beekeeper_settings)

        return await AsyncBeekeeper.factory(settings=self.beekeeper_settings)

    async def _update_node(self) -> None:
        if self._profile is None:
            if self._node is not None:
                self._node.teardown()
            self._node = None
            return

        if self._node is None:
            self._node = Node(self._profile)
        else:
            self._node.change_related_profile(self._profile)

    @classmethod
    def _setup_beekeepy_settings(cls) -> BeekeepySettings:
        return safe_settings.beekeeper.settings_factory()


class TUIWorld(World, CliveDOMNode):
    profile_reactive: Profile = var(None, init=False)  # type: ignore[assignment]
    node_reactive: Node = var(None, init=False)  # type: ignore[assignment]
    app_state: AppState = var(None, init=False)  # type: ignore[assignment]

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

    @property
    def _should_save_profile_on_close(self) -> bool:
        """In TUI, it's not possible to save profile on some screens like Unlock/CreateProfile."""
        return super()._should_save_profile_on_close and self.app_state.is_unlocked

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

    async def switch_profile(self, new_profile: Profile) -> None:
        await super().switch_profile(new_profile)
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
            self.node_reactive = self._node
        if self._profile is not None:
            self.profile_reactive = self._profile


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
