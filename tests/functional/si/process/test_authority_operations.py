from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import Authority
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_DATA
from schemas.operations.account_update2_operation import AccountUpdate2Operation

from .constants import AMOUNT, MEMO, RECEIVER, TEST_KEY, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    import test_tools as tt

    from clive.si import UnlockedCliveSi


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


async def test_authority_update_add_key_without_threshold(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating active authority by adding a key without changing threshold."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
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
    # Threshold should remain unchanged from the original account authority
    assert operation.active.weight_threshold == 1


async def test_authority_update_modify_key_without_threshold(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test modifying an existing key weight without changing threshold."""
    # ACT
    transaction = (
        await clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .modify_key(
            key=TEST_KEY,
            weight=3,
        )
        .as_transaction_object()
    )

    # ASSERT
    assert len(transaction.operations) == 1
    operation = transaction.operations[0].value
    assert isinstance(operation, AccountUpdate2Operation)
    assert operation.active is not None
    # Threshold should remain unchanged
    assert operation.active.weight_threshold == 1


async def test_authority_update_posting_without_threshold(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating posting authority without setting threshold."""
    # ACT
    transaction = (
        await clive_si.process.update_posting_authority(
            account_name=WORKING_ACCOUNT_NAME,
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
    # Threshold should remain unchanged from original
    assert operation.posting.weight_threshold == 1


async def test_authority_update_owner_without_threshold(
    clive_si: UnlockedCliveSi,
) -> None:
    """Test updating owner authority without setting threshold."""
    # ACT
    transaction = (
        await clive_si.process.update_owner_authority(
            account_name=WORKING_ACCOUNT_NAME,
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
    # Threshold should remain unchanged from original
    assert operation.owner.weight_threshold == 1


async def test_authority_update_broadcast_add_key(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting authority update with new key."""
    # ACT
    await (
        clive_si.process.update_active_authority(
            account_name=WORKING_ACCOUNT_NAME,
            threshold=1,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .autosign()
        .broadcast()
    )

    # ASSERT - verify the key was added to the account
    account = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME)
    assert account is not None
    # The authority should now contain TEST_KEY
    key_found = any(TEST_KEY in str(key_auth) for key_auth in account.active.key_auths)
    assert key_found, f"Key {TEST_KEY} not found in active authority"


async def test_authority_update_broadcast_without_threshold(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting authority update without changing threshold."""
    # ARRANGE - get original threshold
    account_before = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME)
    assert account_before is not None, "Account should exist"
    original_threshold = account_before.posting.weight_threshold

    # ACT
    await (
        clive_si.process.update_posting_authority(
            account_name=WORKING_ACCOUNT_NAME,
        )
        .add_key(
            key=TEST_KEY,
            weight=1,
        )
        .autosign()
        .broadcast()
    )

    # ASSERT - verify threshold unchanged and key added
    account_after = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME)
    assert account_after is not None, "Account should exist"
    assert account_after.posting.weight_threshold == original_threshold
    key_found = any(TEST_KEY in str(key_auth) for key_auth in account_after.posting.key_auths)
    assert key_found, f"Key {TEST_KEY} not found in posting authority"


async def test_authority_update_broadcast_with_transfer(
    clive_si: UnlockedCliveSi,
    node: tt.RawNode,
) -> None:
    """Test broadcasting combined authority update and transfer in one transaction."""
    expected_balance_after = WORKING_ACCOUNT_DATA.hives_liquid - AMOUNT

    # ACT
    await (
        clive_si.process.update_active_authority(
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
        .autosign()
        .broadcast()
    )

    # ASSERT - verify both operations were executed
    account = node.api.wallet_bridge.get_account(WORKING_ACCOUNT_NAME)
    assert account is not None, "Account should exist"

    # Verify key was added to active authority
    key_found = any(TEST_KEY in str(key_auth) for key_auth in account.active.key_auths)
    assert key_found, f"Key {TEST_KEY} not found in active authority"

    # Verify transfer was executed by checking balance
    balance_after = account.balance
    assert balance_after == expected_balance_after
