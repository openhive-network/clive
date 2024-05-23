from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from clive.__private.core.constants import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from clive.models import Asset


@dataclass
class Manabar:
    value: Asset.Hive
    max_value: Asset.Hive
    full_regeneration: timedelta

    @property
    def percentage(self) -> Decimal:
        precision = HIVE_PERCENT_PRECISION_DOT_PLACES

        if self.max_value <= 0:
            return DecimalConverter.convert(0, precision=precision)

        raw_value = Decimal(self.value.amount)
        raw_max_value = Decimal(self.max_value.amount)
        percentage = raw_value * 100 / raw_max_value
        return DecimalConverter.round_to_precision(percentage, precision=precision)


@dataclass(kw_only=True)
class NodeData:
    hbd_balance: Asset.Hbd
    hbd_savings: Asset.Hbd
    hbd_unclaimed: Asset.Hbd
    hive_balance: Asset.Hive
    hive_savings: Asset.Hive
    hive_unclaimed: Asset.Hive
    hp_balance: int
    proxy: str
    hp_unclaimed: Asset.Vests
    last_refresh: datetime
    last_history_entry: datetime
    last_account_update: datetime
    recovery_account: str
    reputation: int
    warnings: int
    vote_manabar: Manabar
    downvote_manabar: Manabar
    rc_manabar: Manabar = field(default_factory=Manabar)
