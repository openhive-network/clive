from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from clive.models import Asset


def default_hive() -> Asset.Hive:
    return Asset.hive(0)


def default_hbd() -> Asset.Hbd:
    return Asset.hbd(0)


def default_vests() -> Asset.Vests:
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
    hbd_balance: Asset.Hbd = field(default_factory=default_hbd)
    hbd_savings: Asset.Hbd = field(default_factory=default_hbd)
    hbd_unclaimed: Asset.Hbd = field(default_factory=default_hbd)
    hive_balance: Asset.Hive = field(default_factory=default_hive)
    hive_savings: Asset.Hive = field(default_factory=default_hive)
    hive_unclaimed: Asset.Hive = field(default_factory=default_hive)
    hp_balance: int = 0
    hp_unclaimed: Asset.Vests = field(default_factory=default_vests)
    last_refresh: datetime = field(default_factory=lambda: datetime.now())
    last_history_entry: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))
    last_account_update: datetime = field(default_factory=lambda: datetime.utcfromtimestamp(0))
    recovery_account: str = ""
    reputation: int = 0
    warnings: int = 0
    rc_manabar: Manabar = field(default_factory=Manabar)
    vote_manabar: Manabar = field(default_factory=Manabar)
    downvote_manabar: Manabar = field(default_factory=Manabar)
