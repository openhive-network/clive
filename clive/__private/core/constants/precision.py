from __future__ import annotations

from math import floor, log10
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

HIVE_PERCENT_PRECISION: Final[int] = 100
HIVE_PERCENT_PRECISION_DOT_PLACES: Final[int] = floor(log10(HIVE_PERCENT_PRECISION))

VESTS_TO_HIVE_RATIO_PRECISION: Final[int] = 1000
VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES: Final[int] = floor(log10(VESTS_TO_HIVE_RATIO_PRECISION))
