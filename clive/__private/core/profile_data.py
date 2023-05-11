from __future__ import annotations

import shelve
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final

from clive.__private import config
from clive.__private.core.beekeeper.handle import ErrorResponseError
from clive.__private.core.beekeeper.model import JSONRPCRequest
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.communication import Communication
from clive.__private.storage.contextual import Context
from clive.__private.storage.mock_database import Account, PrivateKey, WorkingAccount
from clive.core.url import Url
from clive.exceptions import CliveError
from clive.models.operation import Operation

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


class Cart(list[Operation]):
    def swap(self, index_1: int, index_2: int) -> None:
        self[index_1], self[index_2] = self[index_2], self[index_1]


@dataclass
class ProfileData(Context):
    _LAST_USED_IDENTIFIER: Final[str] = field(init=False, default="!last_used")

    name: str = ""

    # TODO: Should be None if not set, since we'll allow for using app without a working account
    working_account: WorkingAccount = field(default_factory=lambda: WorkingAccount("", []))
    watched_accounts: list[Account] = field(default_factory=list)
    cart = Cart()

    backup_node_addresses: list[Url] = field(init=False)
    node_address: Url = field(init=False)

    @property
    def chain_id(self) -> str:
        chain_id: str = config.settings.get("node.chain_id")
        if bool(chain_id):
            return chain_id
        assert self.node_address
        config.settings["node.chain_id"] = Communication.request(
            self.node_address.as_string(),
            data=JSONRPCRequest(method="database_api.get_config", params={}).dict(by_alias=True),
        ).json()["result"]["HIVE_CHAIN_ID"]
        return self.chain_id

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

        with shelve.open(str(self._get_file_storage_path())) as db:
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
        cls._get_file_storage_path().parent.mkdir(parents=True, exist_ok=True)

        with shelve.open(str(cls._get_file_storage_path())) as db:
            if name is None:
                name = db.get(cls._LAST_USED_IDENTIFIER, "")
            return db.get(name, cls(name))

    @classmethod
    def list_profiles(cls) -> list[str]:
        with shelve.open(str(cls._get_file_storage_path())) as db:
            return list(db.keys() - {cls._LAST_USED_IDENTIFIER})

    @staticmethod
    def __default_node_address() -> list[Url]:
        return [
            Url("https", "api.hive.blog"),
            Url("http", "localhost", 8090),
            Url("http", "hive-6.pl.syncad.com", 18090),
        ]

    def write_to_beekeeper(self, beekeeper: Beekeeper, password: str) -> None:
        try:
            beekeeper.api.open(wallet_name=self.name)
            with suppress(CliveError):  # make sure wallet is open
                beekeeper.api.unlock(wallet_name=self.name, password=password)
        except ErrorResponseError:
            beekeeper.api.create(wallet_name=self.name, password=password)

        for i, key in enumerate(self.working_account.keys):
            if isinstance(key, PrivateKey):
                self.working_account.keys[i] = ImportKey.execute_with_result(
                    ImportKey(wallet=self.name, key_to_import=key, beekeeper=beekeeper)
                )
