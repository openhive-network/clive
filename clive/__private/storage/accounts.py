from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from clive.__private.core.keys import KeyManager
from clive.__private.storage.mock_database import NodeData


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


@dataclass
class Account:
    name: str
    data: NodeData = field(default_factory=NodeData)

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class WorkingAccount(Account):
    keys: KeyManager = field(default_factory=KeyManager)

    def __hash__(self) -> int:
        return super().__hash__()
