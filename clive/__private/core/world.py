from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer
from textual.reactive import var

from clive.__private.core.app_state import AppState
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.commands import Commands, TextualCommands
from clive.__private.core.node.node import Node
from clive.__private.core.profile_data import ProfileData, ProfileDoesNotExistsError
from clive.__private.ui.background_tasks import BackgroundTasks
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from clive.core.url import Url


class World:
    """
    World is a top-level container for all application objects.

    It is a single source of truth for interacting with the Clive application.

    Args:
    ----
    profile_name: Name of the profile to load. If empty string is passed, the lastly used profile is loaded.
    use_beekeeper: If True, there will be access to beekeeper. If False, beekeeper will not be available.
    beekeeper_remote_endpoint: If given, remote beekeeper will be used. If not given, local beekeeper will start.
    """

    def __init__(
        self,
        profile_name: str = "",
        use_beekeeper: bool = True,
        beekeeper_remote_endpoint: Url | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._profile_data = self._load_profile(profile_name)
        self._app_state = AppState(self)
        self._commands = self._setup_commands()
        self._background_tasks = BackgroundTasks()

        if use_beekeeper:
            self._beekeeper: Beekeeper | None = self.__setup_beekeeper(remote_endpoint=beekeeper_remote_endpoint)
        else:
            self._beekeeper = None

        self._node = Node(self._profile_data)

    @property
    def commands(self) -> Commands[World]:
        return self._commands

    @property
    def background_tasks(self) -> BackgroundTasks:
        return self._background_tasks

    @property
    def beekeeper(self) -> Beekeeper:
        assert self._beekeeper is not None, "Beekeeper is not initialized"
        return self._beekeeper

    @property
    def node(self) -> Node:
        return self._node

    def close(self) -> None:
        if self._beekeeper is not None:
            self._beekeeper.close()

    def _load_profile(self, profile_name: str) -> ProfileData:
        return ProfileData.load(profile_name)

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    def __setup_beekeeper(self, *, remote_endpoint: Url | None = None) -> Beekeeper:
        keeper = Beekeeper(remote_endpoint=remote_endpoint)
        keeper.start()
        return keeper

    @property
    def profile_data(self) -> ProfileData:
        return self._profile_data

    @property
    def app_state(self) -> AppState:
        return self._app_state


class TextualWorld(World, CliveWidget, ManualReactive):
    profile_data: ProfileData = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__(ProfileData.get_lastly_used_profile_name() or ProfileData.ONBOARDING_PROFILE_NAME)
        self.profile_data = self._profile_data
        self.app_state = self._app_state
        self.node = self._node

    def _setup_commands(self) -> TextualCommands:  # type: ignore[override]
        return TextualCommands(self)


class TyperWorld(World):
    def _load_profile(self, profile_name: str) -> ProfileData:
        try:
            return ProfileData.load(profile_name, auto_create=False)
        except ProfileDoesNotExistsError as error:
            raise typer.BadParameter(str(error)) from None
