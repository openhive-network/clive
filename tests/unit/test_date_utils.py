from __future__ import annotations

from datetime import timedelta

import pytest

from clive.__private.core.date_utils import timedelta_to_int_hours


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
