from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter
from clive.__private.models.disabled_api import DisabledAPI

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from clive.__private.models.asset import Asset
    from clive.__private.models.hp_vests_balance import HpVestsBalance


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
    owned_hp_balance: HpVestsBalance
    unclaimed_hp_balance: HpVestsBalance
    proxy: str
    last_refresh: datetime
    last_history_entry: datetime
    last_account_update: datetime
    pending_claimed_accounts: int
    recovery_account: str
    governance_vote_expiration_ts: datetime
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
