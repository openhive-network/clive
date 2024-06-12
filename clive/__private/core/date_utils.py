from __future__ import annotations

from datetime import datetime, timedelta, timezone


def is_null_date(value: datetime) -> bool:
    _value = value.replace(tzinfo=None)
    epoch_time = datetime(1970, 1, 1, 0, 0, 0)  # noqa: DTZ001 TODO: maybe should compare UTC only
    second_before_epoch_time = epoch_time - timedelta(seconds=1)
    return _value in (epoch_time, second_before_epoch_time)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_from_timestamp(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def utc_epoch() -> datetime:
    return utc_from_timestamp(0)
