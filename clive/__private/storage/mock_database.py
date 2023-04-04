from __future__ import annotations

import random
import shelve
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Final
from urllib.parse import urlparse

import clive.__private.config as config  # noqa: PLR0402 # it is patched in tests
from clive.__private.core.operations_cart import OperationsCart
from clive.exceptions import NodeAddressError, PrivateKeyError

if TYPE_CHECKING:
    from pathlib import Path


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


@dataclass
class Account:
    name: str


@dataclass
class PrivateKey:
    key_name: str
    key: str
    file_path: Path | None = None

    @classmethod
    def from_file(cls, key_name: str, file_path: Path) -> PrivateKey:
        key = cls.read_key_from_file(file_path)
        return cls(key_name, key, file_path)

    @classmethod
    def read_key_from_file(cls, file_path: Path) -> str:
        return file_path.read_text().strip()

    @staticmethod
    def validate_key(key: str) -> str:
        if key == "error":
            raise PrivateKeyError(key)
        return key

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, PrivateKey):
            return self.key == __value.key and self.key_name == __value.key_name
        return super().__eq__(__value)


@dataclass
class WorkingAccount(Account):
    keys: list[PrivateKey]


@dataclass
class NodeAddress:
    proto: str
    host: str
    port: int | None = None

    def __str__(self) -> str:
        return f"{self.proto}://{self.host}" + ("" if self.port is None else f":{self.port}")

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def parse(cls, address: str) -> NodeAddress:
        try:
            url = urlparse(address)
            if url.hostname is None:
                raise ValueError  # noqa TRY301 TODO: Refactor
        except ValueError:
            raise NodeAddressError(f"Invalid address: {address}") from None
        else:
            return cls(url.scheme, str(url.hostname), url.port)


@dataclass
class NodeData:
    reputation: float = random.uniform(0, 100)
    hive_balance: float = random.uniform(0, 100)
    hive_power_balance: float = random.uniform(0, 100)
    hive_dollars: float = random.uniform(0, 100)
    hive_savings: float = random.uniform(0, 100)
    hbd_savings: float = random.uniform(0, 100)
    hbd_unclaimed: float = random.uniform(0, 100)
    hp_unclaimed: float = random.uniform(0, 100)
    hive_unclaimed: float = random.uniform(0, 100)
    rc: int = random.randint(0, 100)
    voting_power: int = random.randint(0, 100)
    down_vote_power: int = random.randint(0, 100)

    last_refresh: datetime = datetime.now()

    def recalc(self) -> None:
        self.last_refresh: datetime = datetime.now()

        for key, value in self.__dict__.items():
            if isinstance(value, float):
                setattr(self, key, random.uniform(0, 100))
            elif isinstance(value, int):
                setattr(self, key, random.randint(0, 100))


@dataclass
class ProfileData:
    _STORAGE_FILE_PATH: Final[Path] = field(init=False, default=config.DATA_DIRECTORY / "profile_data")
    _LAST_USED_IDENTIFIER: Final[str] = field(init=False, default="!last_used")

    name: str = ""
    password: str = ""  # yes, yes, plaintext

    # TODO: Should be None if not set, since we'll allow for using app without a working account
    working_account: WorkingAccount = field(default_factory=lambda: WorkingAccount("", []))
    watched_accounts: list[Account] = field(default_factory=list)
    operations_cart = OperationsCart()

    backup_node_addresses: list[NodeAddress] = field(init=False)
    node_address: NodeAddress = field(init=False)

    def __post_init__(self) -> None:
        self.backup_node_addresses = self.__default_node_address()
        self.node_address = self.backup_node_addresses[0]

    def save(self) -> None:
        from clive.__private.ui.app import clive_app

        clive_app.update_reactive("profile_data")

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
