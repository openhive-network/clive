from __future__ import annotations

import random
import shelve
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from clive.config import DATA_DIRECTORY


class AccountType(str, Enum):
    value: str

    ACTIVE = "active"
    WATCHED = "watched"


@dataclass
class Account:
    name: str


@dataclass
class PrivateKey:
    key_name: str
    key: str


@dataclass
class ActiveAccount(Account):
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

    active_account: ActiveAccount = ActiveAccount(
        "MAIN_ACCOUNT" * 4, [PrivateKey("default", "X" * 14), PrivateKey("memo", "Y" * 14)]
    )
    backup_node_addresses: list[NodeAddress] = [
        NodeAddress("https", "api.hive.blog"),
        NodeAddress("http", "localhost", 8090),
        NodeAddress("http", "hive-6.pl.syncad.com", 18090),
    ]
    node_address: NodeAddress = backup_node_addresses[0]
    watched_accounts: list[Account] = [Account(f"WATCHED_ACCOUNT_{i}") for i in range(10)]

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
