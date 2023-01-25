
from dataclasses import dataclass
from enum import IntEnum
from typing import List

class AccountType(IntEnum):
    ACTIVE = 0
    WATCHED = 1

@dataclass
class Account:
    name: str
    account_type: AccountType
    key_names: Optional[List[str]]


class MockDB:
    ACCOUNTS: List[Account] = [
        Account("A"*4, AccountType.ACTIVE, ["0"*14, "1"*14]),
        Account("B"*4, AccountType.WATCHED, None),
        Account("C"*4, AccountType.ACTIVE, ["0"*14]),
        Account("D"*4, AccountType.WATCHED, None)
    ]
