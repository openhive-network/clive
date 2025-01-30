from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.models import Asset

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.__private.core.iwax import TotalVestingProtocol


def calculate_vests_to_hive_ratio(data: TotalVestingProtocol) -> Decimal:
    ratio = iwax.calculate_hp_to_vests(Asset.hive(1), data)
    return Asset.as_decimal(ratio)
