from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain

from .constants import (
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


async def test_transfer_simple(
    clive_si: Profile,
    node: tt.RawNode,
) -> None:
    """Test simple transfer operation with autosign and broadcast."""
    # ARRANGE
    balance_before = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]

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
    assert balance_after == balance_before - AMOUNT


async def test_transfer_as_transaction_object(
    clive_si: Profile,
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
    assert operation.from_ == WORKING_ACCOUNT_NAME  # type: ignore[union-attr]
    assert operation.to == RECEIVER  # type: ignore[union-attr]
    assert operation.amount == AMOUNT  # type: ignore[union-attr]
    assert operation.memo == MEMO  # type: ignore[union-attr]


async def test_transfer_sign_and_broadcast_separately(
    clive_si: Profile,
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
    operation = transaction.operations[0].value
    assert_operations_placed_in_blockchain(node, transaction_id, operation)


async def test_transfer_double_in_one_transaction(
    clive_si: Profile,
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
    assert transaction.operations[0].value.to == RECEIVER  # type: ignore[union-attr]
    assert transaction.operations[1].value.to == SECOND_RECEIVER  # type: ignore[union-attr]


async def test_transfer_triple_in_one_transaction(
    clive_si: Profile,
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
    assert transaction.operations[0].value.to == RECEIVER  # type: ignore[union-attr]
    assert transaction.operations[1].value.to == SECOND_RECEIVER  # type: ignore[union-attr]
    assert transaction.operations[2].value.to == RECEIVER  # type: ignore[union-attr]


async def test_transfer_save_to_file(
    clive_si: Profile,
    tmp_path: Path,
) -> None:
    """Test saving transfer transaction to file."""
    # ARRANGE
    files_dir = tmp_path / "transactions"
    files_dir.mkdir(parents=True, exist_ok=True)
    file_path = files_dir / "transfer.json"

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
    clive_si: Profile,
) -> None:
    """Test that transfer validation properly catches invalid account names."""
    # ARRANGE - account name too short (minimum is 3 characters)
    invalid_account = "ab"

    # ACT & ASSERT
    with pytest.raises(Exception, match=r"(length|validation)"):
        await clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=invalid_account,
            amount=AMOUNT,
            memo=MEMO,
        ).as_transaction_object()
