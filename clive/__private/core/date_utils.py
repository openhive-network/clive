from __future__ import annotations

from datetime import UTC, datetime, timedelta

from clive.__private.core.constants.date import SECONDS_IN_HOUR


def is_null_date(value: datetime) -> bool:
    _value = value.replace(tzinfo=None)
    epoch_time = datetime(1970, 1, 1, 0, 0, 0)  # noqa: DTZ001 TODO: maybe should compare UTC only
    second_before_epoch_time = epoch_time - timedelta(seconds=1)
    return _value in (epoch_time, second_before_epoch_time)


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_from_timestamp(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=UTC)


def utc_epoch() -> datetime:
    return utc_from_timestamp(0)


def timedelta_to_int_hours(td: timedelta) -> int:
    """
    Convert a timedelta to a hours int representation.

    Args:
        td: The value to convert.

    Example:
        >>> timedelta_to_int_hours(timedelta(days=7))
        168
        >>> timedelta_to_int_hours(timedelta(hours=50))
        50
        >>> timedelta_to_int_hours(timedelta(weeks=1, days=2, hours=3))
        219

    Returns:
        The number of hours.
    """
    return int(td.total_seconds() / SECONDS_IN_HOUR)
