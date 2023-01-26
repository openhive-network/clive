from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional


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
