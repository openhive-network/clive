"""Tests for transaction finalization methods (broadcast, save_file, as_transaction_object)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal

import pytest

from clive_local_tools.helpers import create_transaction_filepath
from schemas.operations.transfer_operation import TransferOperation

from .constants import AMOUNT, MEMO, RECEIVER, WORKING_ACCOUNT_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    import test_tools as tt

    from clive.si import UnlockedCliveSi


def verify_transfer_operation(json_: dict[str, Any], from_: str, to: str, amount: tt.Asset.HiveT, memo: str) -> None:
    """Verify that a JSON transaction contains the expected transfer operation."""
    assert "operations" in json_
    assert len(json_["operations"]) == 1
    saved_operation = json_["operations"][0]

    # Verify the structure: {"type": "transfer_operation", "value": { ... }}
    assert saved_operation["type"] == "transfer_operation"
    assert saved_operation["value"]["from"] == from_
    assert saved_operation["value"]["to"] == to
    assert saved_operation["value"]["amount"] == amount
    assert saved_operation["value"]["memo"] == memo


async def test_broadcast(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting a transfer transaction with autosign."""
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


async def test_broadcast_on_object(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting a transfer transaction with autosign."""
    # ARRANGE
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # ACT
    transfer_transaction = await (
        clive_si.process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .autosign()
        .as_transaction_object()
    )
    await transfer_transaction.broadcast()
    # ASSERT
    balance_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME).balance  # type: ignore[union-attr]
    assert balance_after == expected_balance_after


@pytest.mark.parametrize("file_format", ["json", "bin"])
@pytest.mark.parametrize(
    "serialization_mode",
    [
        pytest.param("legacy", marks=pytest.mark.skip(reason="Legacy not supported")),
        "hf26",
    ],
)
async def test_save_to_file_direct(
    clive_si: UnlockedCliveSi,
    file_format: Literal["json", "bin"],
    serialization_mode: Literal["legacy", "hf26"],
) -> None:
    """Test saving transaction to file directly (without creating transaction object first)."""
    # ARRANGE
    file_path = create_transaction_filepath()

    # ACT
    await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).save_file(path=file_path, file_format=file_format, serialization_mode=serialization_mode)

    # ASSERT
    assert file_path.exists()

    if file_format == "json":
        with file_path.open() as f:
            saved_transaction = json.load(f)

        verify_transfer_operation(saved_transaction, WORKING_ACCOUNT_NAME, RECEIVER, AMOUNT, MEMO)
    else:
        # For binary format, just verify the file exists and has content
        assert file_path.stat().st_size > 0, "Binary file should have content"


@pytest.mark.parametrize("file_format", ["json", "bin"])
@pytest.mark.parametrize(
    "serialization_mode",
    [
        pytest.param("legacy", marks=pytest.mark.skip(reason="Legacy not supported")),
        "hf26",
    ],
)
async def test_save_to_file_on_object(
    clive_si: UnlockedCliveSi,
    file_format: Literal["json", "bin"],
    serialization_mode: Literal["legacy", "hf26"],
) -> None:
    """Test saving transaction to file on transaction object (after calling as_transaction_object)."""
    # ARRANGE
    file_path = create_transaction_filepath()

    # ACT
    transaction = await clive_si.process.transfer(
        from_account=WORKING_ACCOUNT_NAME,
        to_account=RECEIVER,
        amount=AMOUNT,
        memo=MEMO,
    ).as_transaction_object()
    await transaction.save_file(path=file_path, file_format=file_format, serialization_mode=serialization_mode)

    # ASSERT
    assert file_path.exists()

    if file_format == "json":
        with file_path.open() as f:
            saved_transaction = json.load(f)

        verify_transfer_operation(saved_transaction, WORKING_ACCOUNT_NAME, RECEIVER, AMOUNT, MEMO)
    else:
        # For binary format, just verify the file exists and has content
        assert file_path.stat().st_size > 0, "Binary file should have content"


async def test_as_transaction_object(clive_si: UnlockedCliveSi) -> None:
    """Test creating a transaction object without broadcasting or saving."""
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
