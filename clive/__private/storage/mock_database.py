from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from urllib.parse import urlparse

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
class PrivateKeyAlias:
    key_name: str


@dataclass
class PrivateKey(PrivateKeyAlias):
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
        if isinstance(__value, PrivateKeyAlias):
            return self.key_name == __value.key_name
        return super().__eq__(__value)


@dataclass
class WorkingAccount(Account):
    keys: list[PrivateKeyAlias]


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
