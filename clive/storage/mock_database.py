from __future__ import annotations

import random
import shelve
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from urllib.parse import urlparse

from clive.config import DATA_DIRECTORY
from clive.exceptions import NodeAddressError
from clive.models.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from pathlib import Path

    from clive.models.operation import Operation


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
        key = file_path.read_text().strip()
        return cls(key_name, key, file_path)


@dataclass
class WorkingAccount(Account):
    keys: List[PrivateKey]


@dataclass
class NodeAddress:
    proto: str
    host: str
    port: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.proto}://{self.host}" + ("" if self.port is None else f":{self.port}")

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def parse(cls, address: str) -> NodeAddress:
        try:
            url = urlparse(address)
            if url.hostname is None:
                raise ValueError
            return cls(url.scheme, str(url.hostname), url.port)
        except ValueError:
            raise NodeAddressError(f"Invalid address: {address}")


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


class ProfileData:
    name: str = ""
    password: str = ""  # yes, yes, plaintext

    working_account: WorkingAccount = WorkingAccount(
        "MAIN_ACCOUNT" * 4, [PrivateKey("default", "X" * 14), PrivateKey("memo", "Y" * 14)]
    )
    backup_node_addresses: list[NodeAddress] = [
        NodeAddress("https", "api.hive.blog"),
        NodeAddress("http", "localhost", 8090),
        NodeAddress("http", "hive-6.pl.syncad.com", 18090),
    ]
    node_address: NodeAddress = backup_node_addresses[0]
    watched_accounts: list[Account] = [Account(f"WATCHED_ACCOUNT_{i}") for i in range(10)]
    operations_cart: list[Operation] = [
        TransferOperation(
            asset="HIVE",
            from_="anna",
            to=f"acc-{i}",
            amount=f"{random.uniform(0, 100) :.3f}",
            memo=f"transfero numero {i+1}",
        )
        for i in range(5)
    ]

    def save(self) -> None:
        from clive.ui.app import clive_app

        clive_app.update_reactive("profile_data")

        with shelve.open(str(DATA_DIRECTORY / "profile_data")) as db:
            db["profile_data"] = self

    @classmethod
    def load(cls) -> ProfileData:
        # create data directory if it doesn't exist
        DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

        with shelve.open(str(DATA_DIRECTORY / "profile_data")) as db:
            return db.get("profile_data", cls())
