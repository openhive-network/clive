from __future__ import annotations

from datetime import timedelta

import pytest

from clive.__private.core.shorthand_timedelta import (
    shorthand_timedelta_to_timedelta,
    timedelta_to_int_hours,
    timedelta_to_shorthand_timedelta,
)


@pytest.mark.parametrize(
    "td",
    [
        timedelta(weeks=1),
        timedelta(days=2, hours=2),
        timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5),
    ],
)
def test_valid_shorthand_timedelta_conversion(td: timedelta) -> None:
    assert shorthand_timedelta_to_timedelta(timedelta_to_shorthand_timedelta(td)) == td


@pytest.mark.parametrize(
    ("td", "hours"),
    [
        (timedelta(weeks=1), 168),
        (timedelta(weeks=1, hours=2), 170),
        (timedelta(days=2, hours=2), 50),
        (timedelta(weeks=1, days=2), 216),
        (timedelta(seconds=3600), 1),
    ],
)
def test_valid_timedelta_to_int_hours(td: timedelta, hours: int) -> None:
    assert timedelta_to_int_hours(td) == hours
