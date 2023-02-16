from __future__ import annotations

import random
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Any, List, Optional


class AccountType(IntEnum):
    ACTIVE = 0
    WATCHED = 1


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
class DataFromNodeT:
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


class MockDB:
    MAIN_ACTIVE_ACCOUNT: ActiveAccount = ActiveAccount(
        "MAIN_ACCOUNT" * 4, [PrivateKey("default", "X" * 14), PrivateKey("memo", "Y" * 14)]
    )
    ACCOUNTS: List[Account] = [Account(f"WATCHED_ACCOUNT_{i}") for i in range(10)]
    node_address = NodeAddress("https", "api.hive.blog")
    BACKUP_NODE_ADDRESSES: List[NodeAddress] = [
        NodeAddress("http", "localhost", 8090),
        NodeAddress("http", "hive-6.pl.syncad.com", 18090),
    ]
    node = DataFromNodeT()

    def __setattr__(self, key: str, value: Any) -> None:
        """Trigger all watchers when any attribute changes."""
        from clive.ui.app import clive_app

        super().__setattr__(key, value)
        clive_app.mock_db = deepcopy(self)
