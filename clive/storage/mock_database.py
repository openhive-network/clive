from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from random import random
from typing import List, Optional

from clive.exceptions import NoMatch
from clive.get_clive import get_clive


class AccountType(IntEnum):
    ACTIVE = 0
    WATCHED = 1


class Validable(ABC):
    @abstractmethod
    def valid(self) -> None:
        ...


@dataclass
class Account(Validable):
    name: str

    def valid(self) -> None:
        account_name_regex = re.compile(
            r"^((([a-z0-9])[a-z0-9\-]{1,14}([a-z0-9]))(\.([a-z0-9])[a-z0-9\-]{1,14}([a-z0-9]))*)$"
        )
        if account_name_regex.match(self.name) is None:
            raise NoMatch(self.name, account_name_regex.pattern)


@dataclass
class PrivateKey(Validable):
    key_name: str
    key: str

    def valid(self) -> None:
        private_key_regex = re.compile(r"^([\dA-Za-z]{51})$")
        if private_key_regex.match(self.key) is None:
            raise NoMatch(self.key, private_key_regex.pattern)


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


def rand(value: float, x_min: float = 10, x_max: float = 10_000) -> float:
    x = value * (1.0 + (0.5 - random()))
    if x >= x_min and x <= x_max:
        return x
    return value


@dataclass
class DataFromNodeT:
    reputation: float = rand(100)
    hive_balance: float = rand(100.0)
    hive_power_balance: float = rand(100.0)
    hive_dollars: float = rand(100.0)
    hive_savings: float = rand(100.0)
    hbd_savings: float = rand(100.0)
    hbd_unclaimed: float = rand(100.0)
    hp_unclaimed: float = rand(100.0)
    hive_unclaimed: float = rand(100.0)
    rc: int = int(rand(10, 10, 90))
    voting_power: float = rand(100.0)
    down_vote_power: float = rand(100.0)

    last_refresh: datetime = datetime.now()

    def recalc(self) -> None:
        if (datetime.now() - self.last_refresh).seconds < get_clive().REFRESH_INTERVAL:
            return

        self.last_refresh: datetime = datetime.now()

        for key, value in self.__dict__.items():
            if isinstance(value, (int, float)):
                if key != "rc":
                    setattr(self, key, rand(value))
                else:
                    setattr(self, key, rand(value, 10, 90))


class MockDB:
    MAIN_ACTIVE_ACCOUNT: ActiveAccount = ActiveAccount(
        "MAIN_ACCOUNT" * 4, [PrivateKey("default", "X" * 14), PrivateKey("memo", "Y" * 14)]
    )
    ACCOUNTS: List[Account] = [Account(f"WATCHED_ACCOUNT_{i}") for i in range(10)]
    NODE_ADDRESS: Optional[NodeAddress] = NodeAddress("https", "api.hive.blog")
    BACKUP_NODE_ADDRESSES: List[NodeAddress] = [
        NodeAddress("http", "localhost", 8090),
        NodeAddress("http", "hive-6.pl.syncad.com", 18090),
    ]
    node = DataFromNodeT()
