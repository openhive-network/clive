"""Tests for transaction signing operations (autosign, sign_with, multisign)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.helpers import create_transaction_filepath

from .constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    AMOUNT,
    MEMO,
    RECEIVER,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive.si import UnlockedCliveSi


async def test_autosign(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test transaction with autosign."""
    # ACT
    transaction = (
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .autosign()
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.signatures) == 1


async def test_sign_with_key_alias(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test signing transaction with a specific key alias."""
    # ACT
    transfer = (
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    assert len(transfer.signatures) == 1


async def test_multisign(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
) -> None:
    """Test adding multiple signatures to a transaction."""
    # Create transaction with first signature
    transfer = (
        await clive_si_with_two_keys_profile.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .sign_with(key=ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )

    expected_signatures_count = 2
    assert len(transfer.signatures) == expected_signatures_count


async def test_multisign_from_object(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
) -> None:
    """Test adding multiple signatures to a transaction."""
    # Create transaction with first signature
    transfer_to_load = (
        await clive_si_with_two_keys_profile.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .as_transaction_object()
    )

    # ACT - Add second signature
    multisigned_transfer = (
        await clive_si_with_two_keys_profile.process.transaction_from_object(
            from_object=transfer_to_load,
            already_signed_mode="multisign",
        )
        .sign_with(key=ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    expected_signatures_count = 2
    assert len(multisigned_transfer.signatures) == expected_signatures_count


async def test_multisign_from_file(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
) -> None:
    """Test adding signature to transaction loaded from file."""
    # ARRANGE
    file_path = create_transaction_filepath()

    # Save transaction with first signature
    await (
        clive_si_with_two_keys_profile.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .save_file(path=file_path)
    )

    # ACT - Load and add second signature
    multisigned_transfer = (
        await clive_si_with_two_keys_profile.process.transaction(
            from_file=file_path,
            already_signed_mode="multisign",
        )
        .sign_with(key=ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    expected_signatures_count = 2
    assert len(multisigned_transfer.signatures) == expected_signatures_count
