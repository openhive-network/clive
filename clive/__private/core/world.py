from __future__ import annotations

from textual.reactive import var

from clive.__private.core.app_state import AppState
from clive.__private.core.beekeeper import BeekeeperLocal, BeekeeperRemote
from clive.__private.core.beekeeper.executable import BeekeeperNotConfiguredError
from clive.__private.core.commands.commands import Commands
from clive.__private.core.node.node import Node
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.mock_database import NodeData
from clive.__private.ui.background_tasks import BackgroundTasks
from clive.__private.ui.manual_reactive import ManualReactive


class World:
    def __init__(self, profile_name: str | None = None) -> None:
        self._node_data = NodeData()
        self._profile_data = ProfileData.load(profile_name)
        self._app_state = AppState(self)
        self._commands = Commands(self)
        self._background_tasks = BackgroundTasks()
        self._beekeeper = self.__setup_beekeeper()
        self._node = Node(self._profile_data)

    @property
    def commands(self) -> Commands:
        return self._commands

    @property
    def background_tasks(self) -> BackgroundTasks:
        return self._background_tasks

    @property
    def beekeeper(self) -> BeekeeperLocal | BeekeeperRemote:
        return self._beekeeper

    @property
    def node(self) -> Node:
        return self._node

    def close(self) -> None:
        if isinstance(self.beekeeper, BeekeeperLocal):
            self.beekeeper.close()

    def __setup_beekeeper(self) -> BeekeeperLocal | BeekeeperRemote:
        if BeekeeperRemote.get_address_from_settings() is not None:
            return BeekeeperRemote()

        if BeekeeperLocal.get_path_from_settings() is not None:
            __beekeeper = BeekeeperLocal()
            __beekeeper.run()
            return __beekeeper

        raise BeekeeperNotConfiguredError()

    @property
    def node_data(self) -> NodeData:
        return self._node_data

    @property
    def profile_data(self) -> ProfileData:
        return self._profile_data

    @property
    def app_state(self) -> AppState:
        return self._app_state


class TextualWorld(World, ManualReactive):
    node_data: NodeData = var(None)  # type: ignore[assignment]
    profile_data: ProfileData = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]

    def __init__(self, profile_name: str | None = None) -> None:
        super().__init__(profile_name)
        self.node_data = self._node_data
        self.profile_data = self._profile_data
        self.app_state = self._app_state
