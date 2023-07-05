from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.reactive import var

from clive.__private.core.app_state import AppState
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.commands import Commands
from clive.__private.core.node.node import Node
from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.background_tasks import BackgroundTasks
from clive.__private.ui.manual_reactive import ManualReactive

if TYPE_CHECKING:
    from clive.core.url import Url


class World:
    def __init__(
        self,
        profile_name: str | None = None,
        use_beekeeper: bool = True,
        beekeeper_remote_endpoint: Url | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._profile_data = ProfileData.load(profile_name)
        self._app_state = AppState(self)
        self._commands = Commands(self)
        self._background_tasks = BackgroundTasks()

        if use_beekeeper:
            self._beekeeper: Beekeeper | None = self.__setup_beekeeper(remote_endpoint=beekeeper_remote_endpoint)
        else:
            self._beekeeper = None

        self._node = Node(self._profile_data)

    @property
    def commands(self) -> Commands:
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


class TextualWorld(World, ManualReactive):
    profile_data: ProfileData = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]

    def __init__(self, profile_name: str | None = None) -> None:
        super().__init__(profile_name)
        self.profile_data = self._profile_data
        self.app_state = self._app_state
