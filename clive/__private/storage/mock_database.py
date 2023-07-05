from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from clive.__private.core.keys.key_manager import KeyManager
from clive.models import Asset


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


def default_hive() -> Asset.HIVE:
    return Asset.hive(0)


def default_hbd() -> Asset.HBD:
    return Asset.hbd(0)


def default_vests() -> Asset.HIVE:
    return Asset.vests(0)


@dataclass
class Manabar:
    value: int = 0
    max_value: int = 1
    full_regeneration: timedelta = field(default_factory=timedelta)

    @property
    def percentage(self) -> float:
        assert self.max_value > 0
        return (self.value * 100.0) / self.max_value


@dataclass
class NodeData:
    hbd_savings: Asset.HBD = field(default_factory=default_hbd)
    hbd_unclaimed: Asset.HBD = field(default_factory=default_hbd)
    hive_balance: Asset.HIVE = field(default_factory=default_hive)
    hive_dollars: Asset.HBD = field(default_factory=default_hbd)
    hive_power_balance: int = 0
    hive_savings: Asset.HIVE = field(default_factory=default_hive)
    hive_unclaimed: Asset.HIVE = field(default_factory=default_hive)
    hp_unclaimed: Asset.VESTS = field(default_factory=default_vests)
    last_refresh: datetime = field(default_factory=lambda: datetime.now())
    last_transaction: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))
    recovery_account: str = ""
    reputation: int = 0
    warnings: int = 0
    rc_manabar: Manabar = field(default_factory=Manabar)
    vote_manabar: Manabar = field(default_factory=Manabar)
    downvote_manabar: Manabar = field(default_factory=Manabar)


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
