from __future__ import annotations

from datetime import timedelta

import pytest

import wax


def date(*, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> int:
    return int(
        timedelta(days=day, hours=hour, minutes=minute, seconds=second, microseconds=0, milliseconds=0).total_seconds()
    )


@pytest.mark.parametrize(
    ("now", "max_mana", "current_mana", "last_update_time", "expected"),
    [
        (date(day=5), 100, 0, date(day=0), date(day=5)),
        (date(day=5), 100, 50, date(day=2, hour=12), date(day=5)),
        (date(day=5), 100, 80, date(day=4), date(day=5)),
        (date(day=4), 100, 80, date(day=4), date(day=5)),
        (date(day=6), 100, 80, date(day=4), date(day=6)),
        (date(day=3), 100, 20, date(day=1), date(day=5)),
    ],
)
def test_proper_calculate_manabar_full_regeneration_time(
    now: int, max_mana: int, current_mana: int, last_update_time: int, expected: int
) -> None:
    response = wax.calculate_manabar_full_regeneration_time(now, max_mana, current_mana, last_update_time)
    assert not response.exception_message
    assert response.result
    assert int(response.result.decode()) == expected
