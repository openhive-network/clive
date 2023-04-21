from __future__ import annotations

import shelve
from contextlib import suppress
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

from clive.__private import config
from clive.__private.core.beekeeper.handle import BeekeeperRemote
from clive.__private.core.commands import execute_with_result
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.storage.mock_database import Account, NodeAddress, PrivateKey, WorkingAccount
from clive.exceptions import CliveError
from clive.models.operation import Operation

if TYPE_CHECKING:
    from pathlib import Path


class Cart(list[Operation]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


@dataclass
class ProfileData:
    _STORAGE_FILE_PATH: Final[Path] = field(init=False, default=config.settings.data_path / "profile_data")
    _LAST_USED_IDENTIFIER: Final[str] = field(init=False, default="!last_used")

    name: str = ""

    # TODO: Should be None if not set, since we'll allow for using app without a working account
    working_account: WorkingAccount = field(default_factory=lambda: WorkingAccount("", []))
    watched_accounts: list[Account] = field(default_factory=list)
    cart = Cart()

    backup_node_addresses: list[NodeAddress] = field(init=False)
    node_address: NodeAddress = field(init=False)

    def __post_init__(self) -> None:
        self.backup_node_addresses = self.__default_node_address()
        self.node_address = self.backup_node_addresses[0]

    def save(self) -> None:
        from clive.__private.ui.app import Clive

        Clive.app_instance().update_reactive("profile_data")

        with shelve.open(str(self._STORAGE_FILE_PATH)) as db:
            db[self.name] = self
            db[self._LAST_USED_IDENTIFIER] = self.name

    @classmethod
    def load(cls, name: str | None = None) -> ProfileData:
        """
        Load profile data with the given name from the database. If no name is given, the last used profile is loaded.

        :param name: Name of the profile to load.
        :return: Profile data.
        """
        # create data directory if it doesn't exist
        cls._STORAGE_FILE_PATH.mkdir(parents=True, exist_ok=True)

        with shelve.open(str(cls._STORAGE_FILE_PATH)) as db:
            if name is None:
                name = db.get(cls._LAST_USED_IDENTIFIER, "")
            return db.get(name, cls(name))

    @classmethod
    def list_profiles(cls) -> list[str]:
        with shelve.open(str(cls._STORAGE_FILE_PATH)) as db:
            return list(db.keys() - {cls._LAST_USED_IDENTIFIER})

    @staticmethod
    def __default_node_address() -> list[NodeAddress]:
        return [
            NodeAddress("https", "api.hive.blog"),
            NodeAddress("http", "localhost", 8090),
            NodeAddress("http", "hive-6.pl.syncad.com", 18090),
        ]

    def write_to_beekeeper(self, beekeeper: BeekeeperRemote, password: str) -> None:
        try:
            beekeeper.api.open(wallet_name=self.name)
            with suppress(CliveError):  # make sure wallet is open
                beekeeper.api.unlock(wallet_name=self.name, password=password)
        except BeekeeperRemote.ErrorResponseError:
            beekeeper.api.create(wallet_name=self.name, password=password)

        for i, key in enumerate(self.working_account.keys):
            if isinstance(key, PrivateKey):
                self.working_account.keys[i] = execute_with_result(
                    ImportKey(wallet=self.name, key_to_import=key, beekeeper=beekeeper)
                )
