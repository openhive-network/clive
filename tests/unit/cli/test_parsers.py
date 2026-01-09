from __future__ import annotations

import pytest
import typer

from clive.__private.cli.common.parsers import account_name
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD


@pytest.mark.parametrize(
    "raw",
    [
        "alice",
        "alice123",
        "alice.bob",
        "alice-bob",
        PERFORM_WORKING_ACCOUNT_LOAD,
    ],
)
def test_account_name_valid(raw: str) -> None:
    assert account_name(raw) == raw


@pytest.mark.parametrize(
    "raw",
    [
        "ab",
        "a" * 17,
        "Alice",
        "1alice",
        "alice@bob",
    ],
)
def test_account_name_invalid(raw: str) -> None:
    with pytest.raises(typer.BadParameter):
        account_name(raw)
