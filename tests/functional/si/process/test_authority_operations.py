from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.authority.authority import Authority
from schemas.operations.account_update2_operation import AccountUpdate2Operation

from .constants import AMOUNT, MEMO, RECEIVER, TEST_KEY, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive.__private.si.base import UnlockedCliveSi


async def test_authority_update_add_key(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating active authority by adding a key."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, AccountUpdate2Operation)
    assert operation.account == WORKING_ACCOUNT_NAME
    assert operation.active is not None
    assert operation.active.weight_threshold == 1


async def test_authority_update_add_and_remove_key(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating authority by adding and then removing a key."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=2,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .remove_key(
            key=TEST_KEY,
        )
        .as_transaction_object()
    )

    # ASSERT
    expected_weight_threshold = 2
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, AccountUpdate2Operation)
    assert isinstance(operation.active, Authority)
    assert operation.active.weight_threshold == expected_weight_threshold


async def test_authority_update_modify_account(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating active authority by adding an account."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_account(
            account_name=RECEIVER,
            weight=1,
        )
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, AccountUpdate2Operation)
    assert operation.active is not None


async def test_authority_update_modify_key(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test modifying an existing key weight in authority."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .modify_key(
            key=TEST_KEY,
            weight=2,
        )
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.operations) == 1


async def test_authority_update_posting(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating posting authority."""
    # ACT
    transaction = (
        await clive_si.process.update_posting_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, AccountUpdate2Operation)
    assert operation.posting is not None


async def test_authority_update_owner(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating owner authority."""
    # ACT
    transaction = (
        await clive_si.process.update_owner_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, AccountUpdate2Operation)
    assert operation.owner is not None


async def test_authority_with_transfer_in_one_transaction(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test combining authority update and transfer in one transaction."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .process.transfer(
            from_account=WORKING_ACCOUNT_NAME,
            to_account=RECEIVER,
            amount=AMOUNT,
            memo=MEMO,
        )
        .as_transaction_object()
    )

    # ASSERT
    expected_operations_count = 2
    assert len(transaction.operations) == expected_operations_count
