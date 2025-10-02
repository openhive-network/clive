from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


DAYS_IN_YEAR: Final[int] = 365

SECONDS_IN_MINUTE: Final[int] = 60
SECONDS_IN_HOUR: Final[int] = 60 * SECONDS_IN_MINUTE
SECONDS_IN_DAY: Final[int] = 24 * SECONDS_IN_HOUR
SECONDS_IN_WEEK: Final[int] = 7 * SECONDS_IN_DAY

TIME_FORMAT_DAYS: Final[str] = "%Y-%m-%d"
TIME_FORMAT_WITH_SECONDS: Final[str] = f"{TIME_FORMAT_DAYS}T%H:%M:%S"
TIME_FORMAT_WITH_MILLIS: Final[str] = f"{TIME_FORMAT_WITH_SECONDS}.%f"

TRANSACTION_EXPIRATION_TIMEDELTA_DEFAULT: Final[timedelta] = timedelta(minutes=30)
