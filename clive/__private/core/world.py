from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING

from clive.__private.config import settings
from clive.__private.core.app_state import AppState
from clive.__private.core.beekeeper.handle import Beekeeper, BeekeeperRemote
from clive.__private.core.beekeeper.url import Url
from clive.__private.core.commands.commands import Commands
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.mock_database import NodeData
from clive.__private.ui.background_tasks import BackgroundTasks

if TYPE_CHECKING:
    from typing_extensions import Self


class World:
    def __init__(self, profile_name: str | None = None) -> None:
        self.__node_data = NodeData()
        self.__profile_data = ProfileData.load(profile_name)
        self.__app_state = AppState(self)
        self.__commands = Commands(self)
        self.__background_tasks = BackgroundTasks()
        self.__setup_beekeeper()

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

    @property
    def beekeeper(self) -> BeekeeperRemote:
        return self.__beekeeper

    def close(self) -> None:
        if isinstance(self.beekeeper, Beekeeper):
            self.beekeeper.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _: type[Exception] | None, __: Exception | None, ___: TracebackType | None) -> None:
        self.close()


    def __setup_beekeeper(self) -> None:
        beekeeper_path: Path | None = None
        if (beekeeper_config := settings.get("beekeeper")) is not None:
            if (beekeeper_remote_address := beekeeper_config.get("remote_address")) is not None:
                self.__beekeeper = BeekeeperRemote(Url(beekeeper_remote_address))
                return

            if (beekeeper_path_from_settings := beekeeper_config.get("path")) is not None:
                beekeeper_path = Path(beekeeper_path_from_settings)

        self.__beekeeper = Beekeeper(executable=beekeeper_path)
        self.__beekeeper.run()
