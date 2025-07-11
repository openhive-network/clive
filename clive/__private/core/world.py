from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, cast, override

from textual.reactive import var

from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.beekeeper_manager import BeekeeperManager
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.commands.get_unlocked_user_wallet import NoProfileUnlockedError
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.exceptions import ProfileNotLoadedError
from wax.wax_factory import create_hive_chain
from wax.wax_options import WaxChainOptions

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable
    from datetime import timedelta
    from types import TracebackType
    from typing import Self

    from beekeepy.interfaces import HttpUrl

    from clive.__private.core.accounts.accounts import Account
    from wax import IHiveChainInterface


class World:
    """
    World is a top-level container for all application objects.

    It is a single source of truth for interacting with the Clive application.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
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
        self._wax_interface: IHiveChainInterface | None = None

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
        """
        Node shouldn't be used for direct API calls in CLI/TUI. Instead, use commands which also handle errors.

        Raises:
            ProfileNotLoadedError: If the profile is not loaded yet.
        """
        if self._node is None:
            raise ProfileNotLoadedError(
                "World node cannot be accessed before profile is loaded as it is profile dependent."
            )
        return self._node

    @property
    def is_node_available(self) -> bool:
        return self._node is not None

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
    def wax_interface(self) -> IHiveChainInterface:
        if self._wax_interface is None:
            raise ProfileNotLoadedError(
                "Wax interface cannot be accessed before profile is loaded as it is profile dependent."
            )
        return self._wax_interface

    @property
    def _should_save_profile_on_close(self) -> bool:
        return self.is_profile_available

    async def setup(self) -> Self:
        async with self._during_setup():
            await self._setup()
        return self

    async def close(self) -> None:
        async with self._during_closure():
            if self._should_save_profile_on_close:
                await self.commands.save_profile()
            if self.is_node_available:
                self.node.teardown()
            self._beekeeper_manager.teardown()

            await self.app_state.lock()

            self._profile = None
            self._node = None
            self._wax_interface = None

    async def create_new_profile(
        self,
        name: str,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
    ) -> None:
        profile = Profile.create(name, working_account, watched_accounts, known_accounts)
        await self.switch_profile(profile)

    async def create_new_profile_with_wallets(
        self,
        name: str,
        password: str,
        working_account: str | Account | None = None,
        watched_accounts: Iterable[str | Account] | None = None,
        known_accounts: Iterable[str | Account] | None = None,
    ) -> None:
        """
        Create a new profile and wallets in beekeeper in one-go.

        Since beekeeper wallet will be created, profile will be also saved.
        If beekeeper wallet creation fails, profile will not be saved.

        Args:
            name: Name of the profile to create.
            password: Password for the profile's wallets.
            working_account: The working account for the profile.
            watched_accounts: The watched accounts for the profile.
            known_accounts: Accounts to be marked as known in the profile.
        """
        await self.create_new_profile(name, working_account, watched_accounts, known_accounts)

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

    async def set_address(self, address: HttpUrl) -> None:
        await self.node._set_address(address)
        self.wax_interface.endpoint_url = address

    async def switch_profile(self, new_profile: Profile | None) -> None:
        self._profile = new_profile
        await self._update_node()
        await self._update_wax_interface()

    async def on_going_into_locked_mode(self, source: LockSource) -> None:
        """Triggered when the application is going into the locked mode."""
        if self._is_during_setup or self._is_during_closure:
            return
        await self._on_going_into_locked_mode(source)

    async def on_going_into_unlocked_mode(self) -> None:
        """Triggered when the application is going into the unlocked mode."""
        if self._is_during_setup or self._is_during_closure:
            return
        await self._on_going_into_unlocked_mode()

    async def _on_going_into_locked_mode(self, _: LockSource) -> None:
        """Override this method to hook when clive goes into the locked mode."""

    async def _on_going_into_unlocked_mode(self) -> None:
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

    async def _setup(self) -> None:
        await self._beekeeper_manager.setup()

    async def _setup_wax_interface(self) -> None:
        chain_id = await self.node.chain_id
        wax_chain_options = WaxChainOptions(chain_id=chain_id, endpoint_url=self.profile.node_address)
        self._wax_interface = create_hive_chain(wax_chain_options)

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    async def _update_node(self) -> None:
        if not self.is_profile_available:
            if self.is_node_available:
                self.node.teardown()
            self._node = None
            return

        if self.is_node_available:
            self.node.change_related_profile(self.profile)
        else:
            self._node = Node(self.profile)

    async def _update_wax_interface(self) -> None:
        if not self.is_profile_available:
            self._wax_interface = None
            return
        if self._wax_interface:
            self._wax_interface.endpoint_url = self.profile.node_address
        else:
            await self._setup_wax_interface()


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
        return cast("TUICommands", super().commands)

    @property
    def _should_save_profile_on_close(self) -> bool:
        """In TUI, it's not possible to save profile on some screens like Unlock/CreateProfile."""
        return super()._should_save_profile_on_close and self.app_state.is_unlocked

    @override
    async def _setup(self) -> None:
        """
        In TUIWorld we assume that profile (and node) is always loaded when entering context manager.

        It's initialized with None because reactive attribute initialization can't be delayed otherwise.
        """
        await super()._setup()
        try:
            await self.load_profile_based_on_beekepeer()
        except NoProfileUnlockedError:
            await self.switch_profile(None)

    async def switch_profile(self, new_profile: Profile | None) -> None:
        await super().switch_profile(new_profile)
        self._update_profile_related_reactive_attributes()

    def _watch_profile(self, profile: Profile) -> None:
        self.node.change_related_profile(profile)

    async def _on_going_into_locked_mode(self, source: LockSource) -> None:
        await self.app._switch_mode_into_locked(source)

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)

    def _update_profile_related_reactive_attributes(self) -> None:
        # There's no proper way to add some proxy reactive property on textual reactives that could raise error if
        # not set yet, and still can be watched. See: https://github.com/Textualize/textual/discussions/4007

        if not self.is_node_available or not self.is_profile_available:
            assert not self.app_state.is_unlocked, "Profile and node should never be None when unlocked"

        self.node_reactive = self._node  # type: ignore[assignment] # ignore that,  node_reactive shouldn't be accessed before unlocking
        self.profile_reactive = self._profile  # type: ignore[assignment] # ignore that, profile_reactive shouldn't be accessed before unlocking


class CLIWorld(World):
    @property
    def commands(self) -> CLICommands:
        return cast("CLICommands", super().commands)

    @override
    async def _setup(self) -> None:
        await super()._setup()
        try:
            await self.load_profile_based_on_beekepeer()
        except NoProfileUnlockedError:
            await self.switch_profile(None)

    def _setup_commands(self) -> CLICommands:
        return CLICommands(self)
