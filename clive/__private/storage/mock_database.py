from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from clive.__private.core.constants import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter
from clive.__private.core.formatters.data_labels import MISSING_API_LABEL

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
class DisabledAPI:
    missing_api: str

    @property
    def missing_api_text(self) -> str:
        return f"{MISSING_API_LABEL} (missing {self.missing_api})"


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
    vote_manabar: Manabar
    downvote_manabar: Manabar
    rc_manabar: Manabar | DisabledAPI

    @property
    def is_rc_api_missing(self) -> bool:
        return isinstance(self.rc_manabar, DisabledAPI)

    @property
    def rc_manabar_ensure_missing_api(self) -> DisabledAPI:
        assert isinstance(self.rc_manabar, DisabledAPI), "Expected RC manabar to be unavailable."
        return self.rc_manabar

    @property
    def rc_manabar_ensure(self) -> Manabar:
        assert isinstance(self.rc_manabar, Manabar), "Expected RC manabar to be available."
        return self.rc_manabar
