from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from clive.__private.core.constants import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter
from clive.models import Asset


def default_hive() -> Asset.Hive:
    return Asset.hive(0)


def default_hbd() -> Asset.Hbd:
    return Asset.hbd(0)


def default_vests() -> Asset.Vests:
    return Asset.vests(0)


@dataclass
class Manabar:
    value: Asset.Hive = field(default_factory=default_hive)
    max_value: Asset.Hive = field(default_factory=default_hive)
    full_regeneration: timedelta = field(default_factory=timedelta)

    @property
    def percentage(self) -> Decimal:
        precision = HIVE_PERCENT_PRECISION_DOT_PLACES

        if self.max_value <= 0:
            return DecimalConverter.convert(0, precision=precision)

        raw_value = Decimal(self.value.amount)
        raw_max_value = Decimal(self.max_value.amount)
        percentage = raw_value * 100 / raw_max_value
        return DecimalConverter.round_to_precision(percentage, precision=precision)


@dataclass
class NodeData:
    hbd_balance: Asset.Hbd = field(default_factory=default_hbd)
    hbd_savings: Asset.Hbd = field(default_factory=default_hbd)
    hbd_unclaimed: Asset.Hbd = field(default_factory=default_hbd)
    hive_balance: Asset.Hive = field(default_factory=default_hive)
    hive_savings: Asset.Hive = field(default_factory=default_hive)
    hive_unclaimed: Asset.Hive = field(default_factory=default_hive)
    hp_balance: int = 0
    proxy: str = ""
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
