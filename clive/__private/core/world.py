from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator, cast

from textual.reactive import var
from typing_extensions import override

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.beekeeper_manager import BeekeeperManager
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.commands.get_unlocked_user_wallet import NoProfileUnlockedError
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.unlock import Unlock
from clive.exceptions import ProfileNotLoadedError

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import timedelta
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
        self._beekeeper_manager = BeekeeperManager()

        self._node: Node | None = None
        self._is_during_setup = False
        self._is_during_closure = False

    async def __aenter__(self) -> Self:
        return await self.setup()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    @property
    def profile(self) -> Profile:
        if self._profile is None:
            raise ProfileNotLoadedError("World profile cannot be accessed before it is loaded.")
        return self._profile

    @property
    def is_profile_available(self) -> bool:
        return self._profile is not None

    @property
    def node(self) -> Node:
        """Node shouldn't be used for direct API calls in CLI/TUI. Instead, use commands which also handle errors."""
        if self._node is None:
            raise ProfileNotLoadedError(
                "World node cannot be accessed before profile is loaded as it is profile dependent."
            )
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
    def beekeeper_manager(self) -> BeekeeperManager:
        return self._beekeeper_manager

    @property
    def _should_save_profile_on_close(self) -> bool:
        return self._profile is not None

    async def setup(self) -> Self:
        async with self._during_setup():
            await self._beekeeper_manager.setup()
        return self

    async def close(self) -> None:
        async with self._during_closure():
            if self._should_save_profile_on_close:
                await self.commands.save_profile()
            if self._node is not None:
                self._node.teardown()
            self._beekeeper_manager.teardown()

            self.app_state.lock()

            self._profile = None
            self._node = None

    async def create_new_profile(
        self,
        name: str,
        working_account: str | WorkingAccount | None = None,
        watched_accounts: Iterable[WatchedAccount] | None = None,
    ) -> None:
        profile = Profile.create(name, working_account, watched_accounts)
        await self.switch_profile(profile)

    async def create_new_profile_with_wallets(
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
        if create_wallet_wrapper.error_occurred:
            self.profile.delete()
        await self.commands.save_profile()

    async def load_profile_based_on_beekepeer(self) -> None:
        unlocked_user_wallet = (await self.commands.get_unlocked_user_wallet()).result_or_raise
        unlocked_encryption_wallet = (await self.commands.get_unlocked_encryption_wallet()).result_or_raise
        await self.beekeeper_manager.set_wallets(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))

        profile_name = self.beekeeper_manager.name
        profile = (await self.commands.load_profile(profile_name=profile_name)).result_or_raise
        await self.switch_profile(profile)
        await self.commands.sync_state_with_beekeeper()

    async def load_profile(
        self, profile_name: str, password: str, *, time: timedelta | None = None, permanent: bool = True
    ) -> None:
        assert not self.app_state.is_unlocked, "Application is already unlocked"
        (
            await self.commands.unlock(profile_name=profile_name, password=password, time=time, permanent=permanent)
        ).raise_if_error_occurred()
        await self.load_profile_based_on_beekepeer()

    async def switch_profile(self, new_profile: Profile | None) -> None:
        self._profile = new_profile
        await self._update_node()

    def on_going_into_locked_mode(self, source: LockSource) -> None:
        """Triggered when the application is going into the locked mode."""
        if self._is_during_setup or self._is_during_closure:
            return
        self._on_going_into_locked_mode(source)

    def on_going_into_unlocked_mode(self) -> None:
        """Triggered when the application is going into the unlocked mode."""
        if self._is_during_setup or self._is_during_closure:
            return
        self._on_going_into_unlocked_mode()

    def _on_going_into_locked_mode(self, _: LockSource) -> None:
        """Override this method to hook when clive goes into the locked mode."""

    def _on_going_into_unlocked_mode(self) -> None:
        """Override this method to hook when clive goes into the unlocked mode."""

    @asynccontextmanager
    async def _during_setup(self) -> AsyncGenerator[None]:
        self._is_during_setup = True
        try:
            yield
        except Exception:
            await self.close()
            raise
        finally:
            self._is_during_setup = False

    @asynccontextmanager
    async def _during_closure(self) -> AsyncGenerator[None]:
        self._is_during_closure = True
        try:
            yield
        finally:
            self._is_during_closure = False

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

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


class TUIWorld(World, CliveDOMNode):
    profile_reactive: Profile = var(None, init=False)  # type: ignore[assignment]
    """Should be used only after unlocking the profile so it will be available then."""

    node_reactive: Node = var(None, init=False)  # type: ignore[assignment]
    """Should be used only after unlocking the profile so it will be available then."""

    app_state: AppState = var(None, init=False)  # type: ignore[assignment]

    @override
    def __init__(self) -> None:
        super().__init__()
        self.app_state = self._app_state

    @property
    def commands(self) -> TUICommands:
        return cast(TUICommands, super().commands)

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
            await self.switch_profile(None)
        return self

    async def switch_profile(self, new_profile: Profile | None) -> None:
        await super().switch_profile(new_profile)
        self._update_profile_related_reactive_attributes()

    def _watch_profile(self, profile: Profile) -> None:
        self.node.change_related_profile(profile)

    def _on_going_into_locked_mode(self, source: LockSource) -> None:
        if source == "beekeeper_wallet_lock_status_update_worker":
            self.app.notify("Switched to the LOCKED mode due to timeout.", timeout=10)
        self.app.pause_refresh_node_data_interval()
        self.app.pause_refresh_alarms_data_interval()
        self.node.cached.clear()

        async def lock() -> None:
            self._add_welcome_modes()
            await self.app.switch_mode("unlock")
            await self._restart_dashboard_mode()
            await self.switch_profile(None)

        self.app.run_worker(lock())

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)

    def _add_welcome_modes(self) -> None:
        self.app.add_mode("create_profile", CreateProfileForm)
        self.app.add_mode("unlock", Unlock)

    async def _restart_dashboard_mode(self) -> None:
        await self.app.remove_mode("dashboard")
        self.app.add_mode("dashboard", Dashboard)

    def _update_profile_related_reactive_attributes(self) -> None:
        # There's no proper way to add some proxy reactive property on textual reactives that could raise error if
        # not set yet, and still can be watched. See: https://github.com/Textualize/textual/discussions/4007

        if self._node is None or self._profile is None:
            assert not self.app_state.is_unlocked, "Profile and node should never be None when unlocked"

        self.node_reactive = self._node  # type: ignore[assignment] # ignore that,  node_reactive shouldn't be accessed before unlocking
        self.profile_reactive = self._profile  # type: ignore[assignment] # ignore that, profile_reactive shouldn't be accessed before unlocking


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
