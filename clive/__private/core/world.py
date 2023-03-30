from __future__ import annotations

from clive.__private.core.app_state import AppState
from clive.__private.storage.mock_database import NodeData, ProfileData


class World:
    def __init__(self) -> None:
        self.__node_data = NodeData()
        self.__profile_data = ProfileData.load()
        self.__app_state = AppState()

    @property
    def node_data(self) -> NodeData:
        return self.__node_data

    @property
    def profile_data(self) -> ProfileData:
        return self.__profile_data

    @property
    def app_state(self) -> AppState:
        return self.__app_state
