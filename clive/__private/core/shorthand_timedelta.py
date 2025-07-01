from __future__ import annotations

import re
from datetime import timedelta
from typing import Final

from clive.__private.core.constants.date import SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE, SECONDS_IN_WEEK
from clive.exceptions import CliveError

SHORTHAND_TIMEDELTA_EXAMPLE: Final[str] = 'hH - hours, dD - days, wW - weeks e.g. "24h" or "2d 2h"'
TIMEDELTA_EXAMPLE: Final[str] = 'e.g. "timedelta(weeks=1, days=2, hours=3)"'


class ShorthandTimedeltaError(CliveError):
    """Base exception for errors related to shorthand timedelta conversions."""


class InvalidShorthandToTimedeltaError(ShorthandTimedeltaError):
    """Exception raised for invalid shorthand date format inputs."""

    def __init__(self, invalid_input: str) -> None:
        self.invalid_input = invalid_input
        self.message = (
            f"Invalid shorthand date format: `{self.invalid_input}`. Please use {SHORTHAND_TIMEDELTA_EXAMPLE}"
        )
        super().__init__(self.message)


class InvalidTimedeltaToShorthandError(ShorthandTimedeltaError):
    """Exception raised for errors converting timedelta to shorthand format."""

    def __init__(self, invalid_input: timedelta) -> None:
        self.invalid_input = invalid_input
        self.message = (
            f"Could not convert timedelta to shorthand delta: `{self.invalid_input}`. Please use {TIMEDELTA_EXAMPLE}"
        )
        super().__init__(self.message)


def timedelta_to_shorthand_timedelta(td: timedelta) -> str:
    """
    Convert a timedelta to a shorthand date string.

    Examples:
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
        raise InvalidTimedeltaToShorthandError(td)

    return result.strip()


def shorthand_timedelta_to_timedelta(shorthand: str) -> timedelta:
    """
    Convert a shorthand date string to a timedelta.

    Examples:
    --------
        shorthand_date_to_timedelta("1w") -> timedelta(weeks=1)
        shorthand_date_to_timedelta("1W") -> timedelta(weeks=1)
        shorthand_date_to_timedelta("2d 2h") -> timedelta(days=2, hours=2)
        shorthand_date_to_timedelta("2D 2H") -> timedelta(days=2, hours=2)
        shorthand_date_to_timedelta("1w 2d 3h 4m 5s") -> timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5)
        shorthand_date_to_timedelta("1W 2D 3H 4M 5S") -> timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5)
    """
    time_units = {"w": "weeks", "d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
    allowed_units = "".join(time_units.keys())
    regex = rf"^(\d+[{allowed_units}](?:\s\d+[{allowed_units}])*)$"
    pattern = re.compile(regex)
    shorthand_lower = shorthand.lower()
    match = pattern.match(shorthand_lower)

    if not match:
        raise InvalidShorthandToTimedeltaError(shorthand)

    amount_and_units_together = match.group().split()

    time_args = dict.fromkeys(time_units.values(), 0)
    for concatenated in amount_and_units_together:
        value = concatenated[:-1]
        unit = concatenated[-1]
        time_args[time_units[unit]] += int(value)

    return timedelta(**time_args)
