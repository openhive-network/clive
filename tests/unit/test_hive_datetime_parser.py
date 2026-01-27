from __future__ import annotations

from datetime import UTC, datetime

import pytest
import typer

from clive.__private.cli.common.parsers import hive_datetime


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Full format - no defaults applied
        ("2024-01-15T12:30:45", datetime(2024, 1, 15, 12, 30, 45, tzinfo=UTC)),
        ("2024-12-31T23:59:59", datetime(2024, 12, 31, 23, 59, 59, tzinfo=UTC)),
        ("2024-01-01T00:00:00", datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)),
        # Without seconds - defaults to :59
        ("2024-01-15T12:30", datetime(2024, 1, 15, 12, 30, 59, tzinfo=UTC)),
        ("2024-01-15T00:00", datetime(2024, 1, 15, 0, 0, 59, tzinfo=UTC)),
        # Without minutes and seconds - defaults to :59:59
        ("2024-01-15T12", datetime(2024, 1, 15, 12, 59, 59, tzinfo=UTC)),
        ("2024-01-15T00", datetime(2024, 1, 15, 0, 59, 59, tzinfo=UTC)),
        ("2024-01-15T23", datetime(2024, 1, 15, 23, 59, 59, tzinfo=UTC)),
        # Date only - defaults to end of day 23:59:59
        ("2024-01-15", datetime(2024, 1, 15, 23, 59, 59, tzinfo=UTC)),
        ("2024-12-31", datetime(2024, 12, 31, 23, 59, 59, tzinfo=UTC)),
        ("2024-01-01", datetime(2024, 1, 1, 23, 59, 59, tzinfo=UTC)),
    ],
)
def test_valid_datetime_formats(raw: str, expected: datetime) -> None:
    result = hive_datetime(raw)
    assert result == expected, f"Failed to parse '{raw}': expected {expected}, got {result}"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "invalid",
        "2024",
        "2024-01",
        "01-15-2024",  # Wrong order
        "2024/01/15",  # Wrong separator
        "2024-01-15 12:30:45",  # Space instead of T
        "2024-01-15T12:30:45Z",  # With timezone suffix
        "2024-01-15T12:30:45+00:00",  # With timezone offset
        "2024-13-01",  # Invalid month
        "2024-01-32",  # Invalid day
        "2024-01-15T25:00:00",  # Invalid hour
        "2024-01-15T12:60:00",  # Invalid minute
        "2024-01-15T12:00:60",  # Invalid second
    ],
)
def test_invalid_datetime_formats(raw: str) -> None:
    with pytest.raises(typer.BadParameter):
        hive_datetime(raw)
