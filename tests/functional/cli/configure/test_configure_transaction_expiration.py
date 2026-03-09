from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.cli.checkers import assert_output_contains
from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

DEFAULT_EXPIRATION: Final[str] = "30m"


@pytest.mark.parametrize(
    "expiration",
    ["3s", "1m", "5m", "30m", "1h", "2h 30m", "12h", "1d"],
    ids=["min_3s", "1min", "5min", "30min", "1hour", "2h30m", "12hours", "max_24h"],
)
async def test_configure_transaction_expiration(cli_tester: CLITester, expiration: str) -> None:
    """Check if valid transaction expiration values are accepted and reflected in profile."""
    # ACT
    cli_tester.configure_transaction_expiration_set(expiration)

    # ASSERT
    result = cli_tester.show_profile()
    assert_output_contains(f"Transaction expiration: {expiration}", result)


async def test_configure_transaction_expiration_default(cli_tester: CLITester) -> None:
    """Check if the default transaction expiration is shown in profile with (default) annotation."""
    # ASSERT
    result = cli_tester.show_profile()
    assert_output_contains(f"Transaction expiration: {DEFAULT_EXPIRATION} (default)", result)


async def test_configure_transaction_expiration_persists_after_change(cli_tester: CLITester) -> None:
    """Check if the transaction expiration persists after setting it twice."""
    # ACT
    cli_tester.configure_transaction_expiration_set("1h")
    cli_tester.configure_transaction_expiration_set("5m")

    # ASSERT
    result = cli_tester.show_profile()
    assert_output_contains("Transaction expiration: 5m", result)


@pytest.mark.parametrize(
    "expiration",
    ["2s", "1s"],
    ids=["below_min_2s", "below_min_1s"],
)
async def test_negative_configure_transaction_expiration_below_min(cli_tester: CLITester, expiration: str) -> None:
    """Check if setting expiration below minimum (3s) raises an error."""
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="Value must be greater or equal"):
        cli_tester.configure_transaction_expiration_set(expiration)


async def test_negative_configure_transaction_expiration_above_max(cli_tester: CLITester) -> None:
    """Check if setting expiration above maximum (24h) raises an error."""
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="Value must be less or equal"):
        cli_tester.configure_transaction_expiration_set("24h 1s")


async def test_negative_configure_transaction_expiration_invalid_format(cli_tester: CLITester) -> None:
    """Check if setting expiration with invalid format raises an error."""
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match="Incorrect format"):
        cli_tester.configure_transaction_expiration_set("invalid")


async def test_negative_configure_transaction_expiration_zero(cli_tester: CLITester) -> None:
    """Check if setting expiration to zero raises an error."""
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError):
        cli_tester.configure_transaction_expiration_set("0s")


async def test_configure_transaction_expiration_reset(cli_tester: CLITester) -> None:
    """Check if resetting transaction expiration restores the default."""
    # ARRANGE
    cli_tester.configure_transaction_expiration_set("1h")

    # ACT
    cli_tester.configure_transaction_expiration_reset()

    # ASSERT
    result = cli_tester.show_profile()
    assert_output_contains(f"Transaction expiration: {DEFAULT_EXPIRATION} (default)", result)


async def test_configure_transaction_expiration_reset_when_already_default(cli_tester: CLITester) -> None:
    """Check if resetting when already default still shows default."""
    # ACT
    cli_tester.configure_transaction_expiration_reset()

    # ASSERT
    result = cli_tester.show_profile()
    assert_output_contains(f"Transaction expiration: {DEFAULT_EXPIRATION} (default)", result)


async def test_configure_transaction_expiration_show_default_annotation(cli_tester: CLITester) -> None:
    """Check that show profile displays '(default)' only when expiration is reset to default."""
    # ASSERT - initially shows (default)
    result = cli_tester.show_profile()
    assert_output_contains(f"Transaction expiration: {DEFAULT_EXPIRATION} (default)", result)

    # ACT - set custom value
    cli_tester.configure_transaction_expiration_set("1h")

    # ASSERT - no (default) annotation when custom value is set
    result = cli_tester.show_profile()
    assert_output_contains("Transaction expiration: 1h", result)
    assert "(default)" not in result.output
