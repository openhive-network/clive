from __future__ import annotations

from clive.__private.core.app_state import AppState
from clive.__private.core.commands.commands import Commands
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.mock_database import NodeData
from clive.__private.ui.background_tasks import BackgroundTasks


class World:
    def __init__(self, profile_name: str | None = None) -> None:
        self.__node_data = NodeData()
        self.__profile_data = ProfileData.load(profile_name)
        self.__app_state = AppState()
        self.__commands = Commands(self)
        self.__background_tasks = BackgroundTasks()

    @property
    def node_data(self) -> NodeData:
        return self.__node_data

    @property
    def profile_data(self) -> ProfileData:
        return self.__profile_data

    @property
    def app_state(self) -> AppState:
        return self.__app_state

    @property
    def commands(self) -> Commands:
        return self.__commands

    @property
    def background_tasks(self) -> BackgroundTasks:
        return self.__background_tasks
