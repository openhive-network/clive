from __future__ import annotations

import shelve
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from clive.__private import config
from clive.__private.storage.contextual import Context
from clive.__private.storage.mock_database import Account, WorkingAccount
from clive.core.url import Url
from clive.models import Operation

if TYPE_CHECKING:
    from collections.abc import Iterator


class Cart(list[Operation]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


@dataclass
class ProfileData(Context):
    _LAST_USED_IDENTIFIER: Final[str] = field(init=False, default="!last_used")

    name: str = ""

    # TODO: Should be None if not set, since we'll allow for using app without a working account
    working_account: WorkingAccount = field(default_factory=lambda: WorkingAccount(""))
    watched_accounts: list[Account] = field(default_factory=list)
    cart = Cart()

    backup_node_addresses: list[Url] = field(init=False)
    node_address: Url = field(init=False)

    @classmethod
    def _get_file_storage_path(cls) -> Path:
        return Path(config.settings.data_path) / "data/profile"

    def __post_init__(self) -> None:
        self.backup_node_addresses = self.__default_node_address()
        self.node_address = self.backup_node_addresses[0]

    def save(self) -> None:
        from clive.__private.ui.app import Clive

        if Clive.is_app_exist():
            Clive.app_instance().world.update_reactive("profile_data")

        with self.__open_database() as db:
            db[self.name] = self
            db[self._LAST_USED_IDENTIFIER] = self.name

    @classmethod
    def get_lastly_used_profile_name(cls) -> str | None:
        with cls.__open_database() as db:
            return db.get(cls._LAST_USED_IDENTIFIER, None)

    @classmethod
    @contextmanager
    def __open_database(cls) -> Iterator[shelve.Shelf[Any]]:
        path = cls._get_file_storage_path()

        # create data directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with shelve.open(str(path)) as db:
            yield db

    @classmethod
    def load(cls, name: str | None = None) -> ProfileData:
        """
        Load profile data with the given name from the database. If no name is given, the last used profile is loaded.

        :param name: Name of the profile to load.
        :return: Profile data.
        """
        with cls.__open_database() as db:
            if name is None:
                name = db.get(cls._LAST_USED_IDENTIFIER, "")
            return db.get(name, cls(name))

    @classmethod
    def list_profiles(cls) -> list[str]:
        with cls.__open_database() as db:
            return list(db.keys() - {cls._LAST_USED_IDENTIFIER})

    @staticmethod
    def __default_node_address() -> list[Url]:
        return [
            Url("http", "localhost", 8090),
            Url("https", "api.hive.blog"),
            Url("http", "hive-6.pl.syncad.com", 18090),
        ]
