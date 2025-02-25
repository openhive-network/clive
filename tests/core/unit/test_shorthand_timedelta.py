from __future__ import annotations

from datetime import timedelta

import pytest

from clive.__private.core.shorthand_timedelta import (
    InvalidShorthandToTimedeltaError,
    InvalidTimedeltaToShorthandError,
    shorthand_timedelta_to_timedelta,
    timedelta_to_shorthand_timedelta,
)


@pytest.mark.parametrize("upper_case", [True, False])
@pytest.mark.parametrize(
    "td",
    [
        timedelta(weeks=1),
        timedelta(days=2, hours=2),
        timedelta(weeks=1, days=2, hours=3, minutes=4, seconds=5),
    ],
)
def test_valid_shorthand_timedelta_conversion(td: timedelta, *, upper_case: bool) -> None:
    shorthand = timedelta_to_shorthand_timedelta(td)
    if upper_case:
        shorthand = shorthand.upper()
    result_td = shorthand_timedelta_to_timedelta(shorthand)
    assert result_td == td, f"Failed to convert back to original {td} timedelta from {shorthand}."


def test_input_validation_shorthand_to_timedelta() -> None:
    with pytest.raises(InvalidShorthandToTimedeltaError):
        shorthand_timedelta_to_timedelta("4f")


def test_input_validation_timedelta_to_shorthand() -> None:
    with pytest.raises(InvalidTimedeltaToShorthandError):
        timedelta_to_shorthand_timedelta(timedelta(weeks=0, days=0, hours=0, minutes=0, seconds=0))
