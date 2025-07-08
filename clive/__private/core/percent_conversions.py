from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.precision import (
    HIVE_PERCENT_PRECISION,
    HIVE_PERCENT_PRECISION_DOT_PLACES,
)
from clive.__private.core.decimal_conventer import DecimalConverter

if TYPE_CHECKING:
    from decimal import Decimal


def hive_percent_to_percent(hive_percent: int | str) -> Decimal:
    """
    Calculate percent from given hive_percent.

    Args:
        hive_percent: The hive percent value to convert, can be an integer or a string.

    Example:
        1234   -> Decimal("12.34")
        "1234" -> Decimal("12.34")
    """
    return DecimalConverter.convert(hive_percent, precision=HIVE_PERCENT_PRECISION_DOT_PLACES) / HIVE_PERCENT_PRECISION


def percent_to_hive_percent(percent: Decimal) -> int:
    """
    Calculate value from given hive percent.

    Args:
        percent: The percent value to convert, must be a Decimal.

    Example:
        Decimal("12.34") -> 1234
    """
    return int(percent * HIVE_PERCENT_PRECISION)
