from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants import HIVE_PERCENT_PRECISION_DOT_PLACES, PARTICIPATION_CALCULATION_SLOTS_COUNT
from clive.__private.core.decimal_conventer import DecimalConverter

if TYPE_CHECKING:
    from decimal import Decimal


def calculate_participation_count_percent(participation: int) -> Decimal:
    amount = DecimalConverter.convert(100 * participation) / PARTICIPATION_CALCULATION_SLOTS_COUNT
    return DecimalConverter.round_to_precision(amount, HIVE_PERCENT_PRECISION_DOT_PLACES)
