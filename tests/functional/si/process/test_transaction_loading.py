from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.helpers import create_transaction_filepath
from schemas.operations.transfer_operation import TransferOperation

from .constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    AMOUNT,
    AMOUNT2,
    MEMO,
    MEMO2,
    RECEIVER,
    SECOND_RECEIVER,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive.si import UnlockedCliveSi


async def test_transaction_from_file_multisign(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
) -> None:
    """Test loading transaction from file and adding another signature."""
    # ARRANGE
    file_path = create_transaction_filepath()

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
    clive_si: UnlockedCliveSi,
) -> None:
    """Test loading transaction from file and adding another operation."""
    # ARRANGE
    file_path = create_transaction_filepath()

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
    operation_0 = combined_transaction.operations[0].value
    operation_1 = combined_transaction.operations[1].value
    assert isinstance(operation_0, TransferOperation)
    assert isinstance(operation_1, TransferOperation)
    assert operation_0.to == RECEIVER
    assert operation_1.to == SECOND_RECEIVER


async def test_broadcast_transaction_from_file_add_operation(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test loading transaction from file, adding another operation and broadcasting."""
    # ARRANGE
    file_path = create_transaction_filepath()
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT - AMOUNT2

    # Save first transaction
    await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).save_file(path=file_path)

    # ACT - Load from file, add second operation and broadcast
    await (
        clive_si.process.transaction(
            from_file=file_path,
            force_unsign=True,
        )
        .process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=SECOND_RECEIVER,
            amount=AMOUNT2,
            memo=MEMO2,
        )
        .autosign()
        .broadcast()
    )

    # ASSERT
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


async def test_transaction_from_object_multisign(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
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


async def test_transaction_from_object_signature_override(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
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
    clive_si: UnlockedCliveSi,
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
            already_signed_mode="strict",
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
    operation_0 = combined_transaction.operations[0].value
    operation_1 = combined_transaction.operations[1].value
    assert isinstance(operation_0, TransferOperation)
    assert isinstance(operation_1, TransferOperation)
    assert operation_0.to == RECEIVER
    assert operation_1.to == SECOND_RECEIVER


async def test_transaction_from_file_with_add_transfer_original_tapos(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test loading transaction from file and adding another operation. - verification of original TAPOS preserved."""
    # ARRANGE
    file_path = create_transaction_filepath()

    # Save first transaction
    transfer_transaction = (
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .autosign()
        .as_transaction_object()
    )

    await transfer_transaction.save_file(path=file_path)

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
    assert transfer_transaction.ref_block_num == combined_transaction.ref_block_num
    assert transfer_transaction.ref_block_prefix == combined_transaction.ref_block_prefix
    assert transfer_transaction.expiration == combined_transaction.expiration
    assert transfer_transaction.signatures != combined_transaction.signatures


async def test_broadcast_signed_transaction_from_file_with_strict_mode(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting a signed transaction loaded from file with strict mode (no additional signing)."""
    file_path = create_transaction_filepath()
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # Create and save signed transaction
    await (
        clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .save_file(path=file_path)
    )

    # Load and broadcast with original signature (strict mode is default)
    await clive_si.process.transaction(from_file=file_path).broadcast()

    # Verify transaction was broadcasted successfully
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


async def test_broadcast_transaction_from_file_with_signature_override(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting a transaction where original signature is overridden."""
    file_path = create_transaction_filepath()
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # Create and save transaction with signature
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

    # Load and override signature with same key
    await (
        clive_si_with_two_keys_profile.process.transaction(from_file=file_path, already_signed_mode="override")
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .broadcast()
    )

    # Verify transaction was broadcasted successfully
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


async def test_broadcast_signed_transaction_from_object_with_strict_mode(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting a signed transaction loaded from object with strict mode (no additional signing)."""
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # Create signed transaction
    transaction = await (
        clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .as_transaction_object()
    )

    # Load from object and broadcast with original signature (strict mode is default)
    await clive_si.process.transaction_from_object(from_object=transaction).broadcast()

    # Verify transaction was broadcasted successfully
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


async def test_broadcast_unsigned_transaction_from_object_with_signing(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting an unsigned transaction loaded from object by signing it."""
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # Create unsigned transaction
    transaction = await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).as_transaction_object()

    # Load from object and sign during broadcast
    await (
        clive_si.process.transaction_from_object(from_object=transaction, already_signed_mode="override")
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .broadcast()
    )

    # Verify transaction was broadcasted successfully
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


async def test_broadcast_transaction_from_object_with_signature_override_same_key(
    clive_si_with_two_keys_profile: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting a transaction from object where original signature is overridden."""
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # Create transaction with signature
    transaction_1 = await (
        clive_si_with_two_keys_profile.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .sign_with(key=ALT_WORKING_ACCOUNT1_KEY_ALIAS)
        .as_transaction_object()
    )
    signature_1 = transaction_1.signatures
    # Load from object and override signature with same key
    transaction2 = await (
        clive_si_with_two_keys_profile.process.transaction_from_object(
            from_object=transaction_1,
            already_signed_mode="override",
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .as_transaction_object()
    )
    await transaction2.broadcast()
    # Verify transaction was broadcasted successfully
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after

    # Verify that transaction has overridden signature
    assert signature_1 != transaction2.signatures
