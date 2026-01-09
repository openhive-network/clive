from __future__ import annotations

import pytest
import typer

from clive.__private.cli.common.parsers import account_name
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD


def test_account_name_valid_simple() -> None:
    # ARRANGE
    raw = "alice"

    # ACT
    result = account_name(raw)

    # ASSERT
    assert result == "alice"


def test_account_name_valid_with_numbers() -> None:
    # ARRANGE
    raw = "alice123"

    # ACT
    result = account_name(raw)

    # ASSERT
    assert result == "alice123"


def test_account_name_valid_with_dots() -> None:
    # ARRANGE
    raw = "alice.bob"

    # ACT
    result = account_name(raw)

    # ASSERT
    assert result == "alice.bob"


def test_account_name_valid_with_hyphens() -> None:
    # ARRANGE
    raw = "alice-bob"

    # ACT
    result = account_name(raw)

    # ASSERT
    assert result == "alice-bob"


def test_account_name_allows_perform_working_account_load_placeholder() -> None:
    # ARRANGE
    raw = PERFORM_WORKING_ACCOUNT_LOAD

    # ACT
    result = account_name(raw)

    # ASSERT
    assert result == PERFORM_WORKING_ACCOUNT_LOAD


def test_account_name_invalid_too_short() -> None:
    # ARRANGE
    raw = "ab"

    # ACT & ASSERT
    with pytest.raises(typer.BadParameter):
        account_name(raw)


def test_account_name_invalid_too_long() -> None:
    # ARRANGE
    raw = "a" * 17

    # ACT & ASSERT
    with pytest.raises(typer.BadParameter):
        account_name(raw)


def test_account_name_invalid_uppercase() -> None:
    # ARRANGE
    raw = "Alice"

    # ACT & ASSERT
    with pytest.raises(typer.BadParameter):
        account_name(raw)


def test_account_name_invalid_starting_with_number() -> None:
    # ARRANGE
    raw = "1alice"

    # ACT & ASSERT
    with pytest.raises(typer.BadParameter):
        account_name(raw)


def test_account_name_invalid_special_chars() -> None:
    # ARRANGE
    raw = "alice@bob"

    # ACT & ASSERT
    with pytest.raises(typer.BadParameter):
        account_name(raw)
