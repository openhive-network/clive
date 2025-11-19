from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    AMOUNT,
    AMOUNT2,
    MEMO,
    MEMO2,
    RECEIVER,
    SECOND_RECEIVER,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.si.base import Profile


async def test_transaction_from_file_multisign(
    clive_si_with_two_keys_profile: Profile,
    tmp_path: Path,
) -> None:
    """Test loading transaction from file and adding another signature."""
    # ARRANGE
    files_dir = tmp_path / "transactions"
    files_dir.mkdir(parents=True, exist_ok=True)
    file_path = files_dir / "transfer_to_multisign.json"

    # Create and save first transaction with one signature
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
    multisigned_transaction = (
        await clive_si_with_two_keys_profile.process.transaction(
            from_file=file_path,
            already_signed_mode="multisign",
        )
        .sign_with(ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    expected_signatures_count = 2
    assert len(multisigned_transaction.signatures) == expected_signatures_count


async def test_transaction_from_file_add_operation(
    clive_si: Profile,
    tmp_path: Path,
) -> None:
    """Test loading transaction from file and adding another operation."""
    # ARRANGE
    files_dir = tmp_path / "transactions"
    files_dir.mkdir(parents=True, exist_ok=True)
    file_path = files_dir / "transfer_base.json"

    # Save first transaction
    await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).save_file(path=file_path)

    # ACT - Load from file and add second operation
    combined_transaction = (
        await clive_si.process.transaction(
            from_file=file_path,
            force_unsign=True,
        )
        .process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=SECOND_RECEIVER,
            amount=AMOUNT2,
            memo=MEMO2,
        )
        .as_transaction_object()
    )

    # ASSERT
    expected_operations_count = 2
    assert len(combined_transaction.operations) == expected_operations_count
    assert combined_transaction.operations[0].value.to == RECEIVER  # type: ignore[union-attr]
    assert combined_transaction.operations[1].value.to == SECOND_RECEIVER  # type: ignore[union-attr]


async def test_transaction_from_object_multisign(
    clive_si_with_two_keys_profile: Profile,
) -> None:
    """Test loading transaction from object and adding another signature."""
    # Create transaction with one signature
    transfer = (
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
            from_object=transfer,
            already_signed_mode="multisign",
        )
        .sign_with(ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    expected_signatures_count = 2
    assert len(multisigned_transfer.signatures) == expected_signatures_count


async def test_transaction_from_object_override(
    clive_si_with_two_keys_profile: Profile,
) -> None:
    """Test loading transaction from object and overriding signatures."""
    # Create transaction with one signature
    transfer = (
        await clive_si_with_two_keys_profile.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .as_transaction_object()
    )

    # ACT - Override with new signature
    overridden_transfer = (
        await clive_si_with_two_keys_profile.process.transaction_from_object(
            from_object=transfer,
            already_signed_mode="override",
        )
        .sign_with(ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    assert len(overridden_transfer.signatures) == 1


async def test_transaction_from_object_add_operation(
    clive_si: Profile,
) -> None:
    """Test loading transaction from object and adding another operation."""
    # Create first transaction
    transaction1 = await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).as_transaction_object()

    # ACT - Load and add second operation
    combined_transaction = (
        await clive_si.process.transaction_from_object(
            from_object=transaction1,
            already_signed_mode="override",
        )
        .process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=SECOND_RECEIVER,
            amount=AMOUNT2,
            memo=MEMO2,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .as_transaction_object()
    )

    # ASSERT
    expected_operations_count = 2
    assert len(combined_transaction.operations) == expected_operations_count
    assert combined_transaction.operations[0].value.to == RECEIVER  # type: ignore[union-attr]
    assert combined_transaction.operations[1].value.to == SECOND_RECEIVER  # type: ignore[union-attr]
