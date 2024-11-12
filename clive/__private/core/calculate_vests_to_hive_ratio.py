from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.precision import (
    VESTS_TO_HIVE_RATIO_PRECISION,
    VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES,
)
from clive.__private.core.decimal_conventer import DecimalConverter

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.__private.core.iwax import TotalVestingProtocol


def calulcate_vests_to_hive_ratio(data: TotalVestingProtocol) -> Decimal:
    value = int(int(data.total_vesting_shares.amount) / int(data.total_vesting_fund_hive.amount))
    return (
        DecimalConverter.convert(value, precision=VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES)
        / VESTS_TO_HIVE_RATIO_PRECISION
    )
