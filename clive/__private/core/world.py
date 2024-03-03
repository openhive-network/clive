from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from beekeepy import async_beekeeper_factory, async_beekeeper_remote_factory
from beekeepy._interface.exceptions import NoWalletWithSuchNameError
from textual.reactive import var

from clive.__private.config import settings
from clive.__private.core.app_state import AppState
from clive.__private.core.commands.commands import Commands, TextualCommands
from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.exceptions import ScreenNotFoundError
from clive.models.aliased import Node, Session, Settings, UnlockedWallet, Wallet

if TYPE_CHECKING:
    from types import TracebackType

    from beekeepy import AsyncBeekeeper
    from helpy import HttpUrl
    from typing_extensions import Self


class World:
    """
    World is a top-level container for all application objects.

    It is a single source of truth for interacting with the Clive application.

    Args:
    ----
    profile_name: Name of the profile to load. If None is passed, the default profile is loaded.
    use_beekeeper: If True, there will be access to beekeeper. If False, beekeeper will not be available.
    beekeeper_remote_endpoint: If given, remote beekeeper will be used. If not given, local beekeeper will start.
    """

    def __init__(
        self,
        profile_name: str | None = None,
        use_beekeeper: bool = True,
        beekeeper_remote_endpoint: HttpUrl | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._profile_data = self._load_profile(profile_name)
        self._app_state = AppState(self)
        self._commands = self._setup_commands()

        self._use_beekeeper = use_beekeeper
        self._beekeeper_remote_endpoint = beekeeper_remote_endpoint
        self._beekeeper: AsyncBeekeeper | None = None
        self.__session: Session | None = None
        self.__wallet: Wallet | None = None

        self._node = Node(settings=Settings(http_endpoint=self._profile_data.node_address))

    async def __aenter__(self) -> Self:
        return await self.setup()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    @property
    def commands(self) -> Commands[World]:
        return self._commands

    @property
    def beekeeper(self) -> AsyncBeekeeper:
        assert self._beekeeper is not None, "Beekeeper is not initialized"
        return self._beekeeper

    @property
    def session(self) -> Session:
        assert self.__session is not None, "Beekeeper is not initialized"
        return self.__session

    @property
    def wallet(self) -> Wallet:
        assert self.__wallet is not None, "Wallet has never been touched"
        return self.__wallet

    @wallet.setter
    def wallet(self, incoming_wallet: Wallet) -> None:
        self.__wallet = incoming_wallet

    @property
    async def unlocked_wallet(self) -> UnlockedWallet:
        wallet = await self.wallet.unlocked
        assert wallet is not None, "Wallet is not unlocked"
        return wallet

    @property
    def node(self) -> Node:
        return self._node

    async def setup(self) -> Self:
        if self._use_beekeeper:
            self._beekeeper = await self.__setup_beekeeper(remote_endpoint=self._beekeeper_remote_endpoint)
            self.__session = await self.beekeeper.create_session()
            self.__session.on_wallet_locked(self.notify_wallet_closing)
            with contextlib.suppress(NoWalletWithSuchNameError):
                self.__wallet = await self.session.open_wallet(name=self.profile_data.name)
        return self

    async def close(self) -> None:
        self.profile_data.save()
        if self._beekeeper is not None:
            assert self.__session is not None
            await self.__session.close_session()
            self.__session = None
            self._beekeeper.delete()

    def _load_profile(self, profile_name: str | None) -> ProfileData:
        return ProfileData.load(profile_name)

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    async def __setup_beekeeper(self, *, remote_endpoint: HttpUrl | None = None) -> AsyncBeekeeper:
        options = Settings(working_directory=Path(settings.get("data_path")) / "beekeeper")
        if remote_endpoint is not None:
            options.http_endpoint=remote_endpoint
            return async_beekeeper_remote_factory(url_or_settings=options)
        return async_beekeeper_factory(settings=options)

    @property
    def profile_data(self) -> ProfileData:
        return self._profile_data

    @property
    def app_state(self) -> AppState:
        return self._app_state

    async def notify_wallet_closing(self, wallet_names: list[str]) -> None:
        if self.__wallet is None:
            return
        my_wallet_name = self.wallet.name
        for name in wallet_names:
            if my_wallet_name == name:
                self.app_state.deactivate()
                return


class TextualWorld(World, CliveWidget, ManualReactive):
    profile_data: ProfileData = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    def __init__(self) -> None:
        profile_name = (
            ProfileData.get_default_profile_name()
            if ProfileData.is_default_profile_set()
            else ProfileData.ONBOARDING_PROFILE_NAME
        )
        super().__init__(profile_name)
        self.profile_data = self._profile_data
        self.app_state = self._app_state
        self.node = self._node

    def _setup_commands(self) -> TextualCommands:  # type: ignore[override]
        return TextualCommands(self)

    def notify_wallet_closing(self) -> None:
        super().notify_wallet_closing()

        with contextlib.suppress(ScreenNotFoundError):
            self.app.replace_screen("DashboardActive", "dashboard_inactive")

        self.notify("Switched to the INACTIVE mode.", severity="warning", timeout=5)
        self.app.trigger_app_state_watchers()


class TyperWorld(World):
    def _load_profile(self, profile_name: str | None) -> ProfileData:
        return ProfileData.load(profile_name, auto_create=False)
