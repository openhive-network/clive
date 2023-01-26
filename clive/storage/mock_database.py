from dataclasses import dataclass
from enum import IntEnum
from typing import List


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


class MockDB:
    MAIN_ACTIVE_ACCOUNT: ActiveAccount = ActiveAccount(
        "MAIN_ACCOUNT" * 4, [PrivateKey("default", "X" * 14), PrivateKey("memo", "Y" * 14)]
    )
    ACCOUNTS: List[Account] = [Account(f"WATCHED_ACCOUNT_{i}") for i in range(10)]
