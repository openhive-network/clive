from __future__ import annotations

import re
from datetime import timedelta
from typing import Final

from clive.__private.core.constants.date import SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE, SECONDS_IN_WEEK

SHORTHAND_TIMEDELTA_EXAMPLE: Final[str] = 'e.g. "24h" or "2d 2h"'


def timedelta_to_shorthand_timedelta(td: timedelta) -> str:
    """
    Convert a timedelta to a shorthand date string.

    Examples
    --------
        timedelta_to_shorthand_date(timedelta(days=7)) -> "1w"
        timedelta_to_shorthand_date(timedelta(hours=50)) -> "2d 2h"
        timedelta_to_shorthand_date(timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5)) -> "1w 2d 3h 4m 5s"
    """
    total_seconds = int(td.total_seconds())

    weeks, remainder = divmod(total_seconds, SECONDS_IN_WEEK)
    days, remainder = divmod(remainder, SECONDS_IN_DAY)
    hours, remainder = divmod(remainder, SECONDS_IN_HOUR)
    minutes, seconds = divmod(remainder, SECONDS_IN_MINUTE)

    result = ""
    if weeks > 0:
        result += f"{weeks}w "
    if days > 0:
        result += f"{days}d "
    if hours > 0:
        result += f"{hours}h "
    if minutes > 0:
        result += f"{minutes}m "
    if seconds > 0:
        result += f"{seconds}s "

    if not result:
        raise ValueError("Could not convert timedelta to shorthand delta.")

    return result.strip()


def shorthand_timedelta_to_timedelta(shorthand: str) -> timedelta:
    """
    Convert a shorthand date string to a timedelta.

    Examples
    --------
        shorthand_date_to_timedelta("1w") -> timedelta(weeks=1)
        shorthand_date_to_timedelta("2d 2h") -> timedelta(days=2, hours=2)
        shorthand_date_to_timedelta("1w 2d 3h 4m 5s") -> timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5)
    """
    time_units = {"w": "weeks", "d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
    pattern = re.compile(rf"(\d+)([{time_units}])")
    matches = pattern.findall(shorthand.lower())

    if not matches:
        raise ValueError("Invalid shorthand date format")

    time_args = {unit: 0 for unit in time_units.values()}
    for value, unit in matches:
        if unit in time_units:
            time_args[time_units[unit]] += int(value)
        else:
            raise ValueError(f"Invalid unit '{unit}'")

    return timedelta(**time_args)
