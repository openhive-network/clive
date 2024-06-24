from __future__ import annotations

from datetime import timedelta

import pytest

from clive.__private.core.shorthand_timedelta import (
    shorthand_timedelta_to_timedelta,
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
