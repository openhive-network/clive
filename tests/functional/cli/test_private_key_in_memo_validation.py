from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLIPrivateKeyInMemoValidationError
from clive.__private.validators.private_key_in_memo_validator import PrivateKeyInMemoValidator
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
NORMAL_MEMO: Final[str] = "This is a normal memo without any private keys"
EMPTY_MEMO: Final[str] = ""
PRIVATE_KEY_ERROR_MATCH: Final[str] = get_formatted_error_message(
    CLIPrivateKeyInMemoValidationError(PrivateKeyInMemoValidator.PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION)
)


async def test_transfer_with_private_key_in_memo_is_rejected(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with private key in memo is rejected."""
    # ARRANGE
    private_key = WORKING_ACCOUNT_DATA.account.private_key

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=PRIVATE_KEY_ERROR_MATCH):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=private_key,
        )


async def test_transfer_with_watched_account_private_key_in_memo_is_rejected(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with watched account's private key in memo is rejected."""
    # ARRANGE
    watched_account_private_key = WATCHED_ACCOUNTS_DATA[0].account.private_key

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=PRIVATE_KEY_ERROR_MATCH):
        cli_tester.process_transfer(
            from_=WORKING_ACCOUNT_NAME,
            amount=tt.Asset.Hive(1),
            to=RECEIVER,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=watched_account_private_key,
        )


async def test_transfer_with_normal_memo_succeeds(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with normal memo text succeeds."""
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=NORMAL_MEMO,
    )


async def test_transfer_with_empty_memo_succeeds(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with empty memo succeeds."""
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=EMPTY_MEMO,
    )


async def test_transfer_with_corrupted_checksum_key_succeeds(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with key-like but invalid string succeeds (no false positive)."""
    # ARRANGE - generate valid key format but corrupt checksum by changing last character
    valid_key = str(WORKING_ACCOUNT_DATA.account.private_key)
    last_char = valid_key[-1]
    corrupted_char = "A" if last_char != "A" else "B"
    invalid_key_with_bad_checksum = valid_key[:-1] + corrupted_char

    # ACT - should succeed because checksum is invalid
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=invalid_key_with_bad_checksum,
    )


async def test_transfer_with_public_key_in_memo_succeeds(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with public key in memo succeeds (public keys are safe to share)."""
    # ARRANGE
    public_key = WORKING_ACCOUNT_DATA.account.public_key

    # ACT
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=public_key,
    )


async def test_transfer_with_partial_private_key_succeeds(
    cli_tester: CLITester,
) -> None:
    """Check that transfer with partial (truncated) private key succeeds."""
    # ARRANGE - only first half of the private key
    private_key = WORKING_ACCOUNT_DATA.account.private_key
    partial_key = private_key[: len(private_key) // 2]

    # ACT
    cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=tt.Asset.Hive(1),
        to=RECEIVER,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=partial_key,
    )


async def test_savings_deposit_with_private_key_in_memo_is_rejected(
    cli_tester: CLITester,
) -> None:
    """Check that savings deposit with private key in memo is rejected."""
    # ARRANGE
    private_key = WORKING_ACCOUNT_DATA.account.private_key

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=PRIVATE_KEY_ERROR_MATCH):
        cli_tester.process_savings_deposit(
            amount=tt.Asset.Hive(1),
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=private_key,
        )


async def test_savings_withdrawal_with_private_key_in_memo_is_rejected(
    cli_tester: CLITester,
) -> None:
    """Check that savings withdrawal with private key in memo is rejected."""
    # ARRANGE
    private_key = WORKING_ACCOUNT_DATA.account.private_key

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=PRIVATE_KEY_ERROR_MATCH):
        cli_tester.process_savings_withdrawal(
            amount=tt.Asset.Hive(1),
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=private_key,
        )


async def test_transfer_schedule_create_with_private_key_in_memo_is_rejected(
    cli_tester: CLITester,
) -> None:
    """Check that creating scheduled transfer with private key in memo is rejected."""
    # ARRANGE
    private_key = WORKING_ACCOUNT_DATA.account.private_key

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=PRIVATE_KEY_ERROR_MATCH):
        cli_tester.process_transfer_schedule_create(
            to=RECEIVER,
            amount=tt.Asset.Hive(1),
            frequency="24h",
            repeat=2,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=private_key,
        )


async def test_transfer_schedule_modify_with_private_key_in_memo_is_rejected(
    cli_tester: CLITester,
) -> None:
    """Check that modifying scheduled transfer with private key in memo is rejected."""
    # ARRANGE
    private_key = WORKING_ACCOUNT_DATA.account.private_key
    # First create a valid scheduled transfer
    cli_tester.process_transfer_schedule_create(
        to=RECEIVER,
        amount=tt.Asset.Hive(1),
        frequency="24h",
        repeat=2,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
        memo=NORMAL_MEMO,
    )

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=PRIVATE_KEY_ERROR_MATCH):
        cli_tester.process_transfer_schedule_modify(
            to=RECEIVER,
            sign_with=WORKING_ACCOUNT_KEY_ALIAS,
            memo=private_key,
        )
