from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.models.schemas import ValidationError
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.helpers import create_transaction_filepath
from schemas.operations.transfer_operation import TransferOperation

from .constants import (
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
    from clive.__private.si.base import UnlockedCliveSi


async def test_transfer_simple(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test simple transfer operation with autosign and broadcast."""
    # ARRANGE
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # ACT
    await (
        clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .autosign()
        .broadcast()
    )

    # ASSERT
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


async def test_transfer_as_transaction_object(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test creating transfer as transaction object without broadcasting."""
    # ACT
    transaction = await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).as_transaction_object()

    # ASSERT
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, TransferOperation)
    assert operation.from_ == WORKING_ACCOUNT_NAME
    assert operation.to == RECEIVER
    assert operation.amount == AMOUNT
    assert operation.memo == MEMO


async def test_transfer_sign_and_broadcast_separately(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test creating transfer as object, then signing and broadcasting separately."""
    # ACT
    transaction = await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).as_transaction_object()

    await (
        clive_si.process.transaction_from_object(
            from_object=transaction,
            already_signed_mode="override",
        )
        .sign_with(key=WORKING_ACCOUNT_KEY_ALIAS)
        .broadcast()
    )

    # ASSERT
    transaction_id = transaction.with_hash().transaction_id
    assert_operations_placed_in_blockchain(node, transaction_id, *transaction.operations_models)


async def test_transfer_double_in_one_transaction(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test chaining two transfers in one transaction."""
    # ACT
    transaction = (
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
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
    assert len(transaction.operations) == expected_operations_count
    operation_0 = transaction.operations[0].value
    operation_1 = transaction.operations[1].value
    assert isinstance(operation_0, TransferOperation)
    assert isinstance(operation_1, TransferOperation)
    assert operation_0.to == RECEIVER
    assert operation_1.to == SECOND_RECEIVER


async def test_transfer_triple_in_one_transaction(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test chaining three transfers in one transaction."""
    # ACT
    transaction = (
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=SECOND_RECEIVER,
            amount=AMOUNT2,
            memo=MEMO2,
        )
        .process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=tt.Asset.Hive(3),
            memo="Third transfer",
        )
        .as_transaction_object()
    )

    # ASSERT
    expected_operations_count = 3
    assert len(transaction.operations) == expected_operations_count
    operation_0 = transaction.operations[0].value
    operation_1 = transaction.operations[1].value
    operation_2 = transaction.operations[2].value
    assert isinstance(operation_0, TransferOperation)
    assert isinstance(operation_1, TransferOperation)
    assert isinstance(operation_2, TransferOperation)
    assert operation_0.to == RECEIVER
    assert operation_1.to == SECOND_RECEIVER
    assert operation_2.to == RECEIVER


async def test_transfer_save_to_file(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test saving transfer transaction to file."""
    # ARRANGE
    file_path = create_transaction_filepath()

    # ACT
    await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).save_file(path=file_path)

    # ASSERT
    assert file_path.exists()


async def test_transfer_validation_error(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test that transfer validation properly catches invalid account names."""
    # ARRANGE - account name too short (minimum is 3 characters)
    invalid_account = "ab"

    # ACT & ASSERT
    with pytest.raises(ValidationError, match="length"):
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=invalid_account,
            amount=AMOUNT,
            memo=MEMO,
        ).as_transaction_object()
