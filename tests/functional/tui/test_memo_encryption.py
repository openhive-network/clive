from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

import pytest
import test_tools as tt

from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import (
    TransferFromSavingsOperation,
    TransferOperation,
    TransferToSavingsOperation,
)
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.screens.operations import Operations, TransferToAccount
from clive.__private.ui.screens.operations.bindings.memo_encrypting_operation_action_bindings import (
    MEMO_KEY_NOT_IMPORTED_WARNING,
)
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.helpers import get_operation_from_transaction
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)
from clive_local_tools.tui.checkers import assert_is_screen_active
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    write_text,
)
from clive_local_tools.tui.utils import log_current_view
from tests.functional.tui.test_savings import fill_savings_data, go_to_savings
from tests.functional.tui.test_transfer import fill_transfer_data

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot

SENDER: Final[str] = WORKING_ACCOUNT_DATA.account.name
RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
ENCRYPTED_MEMO_CONTENT: Final[str] = "#This is a secret memo"
PLAIN_MEMO_CONTENT: Final[str] = "This is a plain memo"
NON_EXISTENT_ACCOUNT: Final[str] = "nonexistent"

SavingsOperationT = TransferToSavingsOperation | TransferFromSavingsOperation
OperationWithMemoT = TransferOperation | SavingsOperationT


def get_notification_messages(pilot: ClivePilot) -> list[str]:
    """Get all notification messages from the pilot app."""
    return [notification.message for notification in pilot.app._notifications]


async def test_transfer_with_encrypted_memo(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """Test that memo is encrypted when it starts with '#' in transfer operation."""
    node, _, pilot = prepared_tui_on_dashboard

    # ACT
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)
    await fill_transfer_data(pilot, RECEIVER, AMOUNT, ENCRYPTED_MEMO_CONTENT)

    log_current_view(pilot.app, nodes=True)

    await focus_next(pilot)  # Go to `Add to cart` button
    await process_operation(pilot, "FINALIZE_TRANSACTION")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    op = get_operation_from_transaction(node, transaction_id, TransferOperation)
    assert op.memo.startswith("#"), "Encrypted memos should start with '#'"
    assert len(op.memo) > len(ENCRYPTED_MEMO_CONTENT), "Encrypted memo should be longer than original"


@pytest.mark.parametrize("operation_type", get_args(SavingsOperationT))
async def test_savings_with_encrypted_memo(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_type: type[SavingsOperationT],
) -> None:
    """Test that memo is encrypted when it starts with '#' in savings operations."""
    node, _, pilot = prepared_tui_on_dashboard

    # ACT
    await go_to_savings(pilot)
    await fill_savings_data(pilot, operation_type, RECEIVER, AMOUNT, ENCRYPTED_MEMO_CONTENT)

    log_current_view(pilot.app, nodes=True)

    await focus_next(pilot)  # Go to `Add to cart` button
    await process_operation(pilot, "FINALIZE_TRANSACTION")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    op = get_operation_from_transaction(node, transaction_id, operation_type)
    assert op.memo.startswith("#"), "Encrypted memos should start with '#'"
    assert len(op.memo) > len(ENCRYPTED_MEMO_CONTENT), "Encrypted memo should be longer than original"


@pytest.mark.parametrize(
    "expected_operation",
    [
        TransferOperation(from_=SENDER, to=RECEIVER, amount=AMOUNT, memo=PLAIN_MEMO_CONTENT),
        TransferToSavingsOperation(from_=SENDER, to=RECEIVER, amount=AMOUNT, memo=PLAIN_MEMO_CONTENT),
        TransferFromSavingsOperation(
            from_=SENDER,
            to=RECEIVER,
            amount=AMOUNT,
            memo=PLAIN_MEMO_CONTENT,
            request_id=WORKING_ACCOUNT_DATA.from_savings_transfer_count,
        ),
    ],
)
async def test_transfer_with_plain_memo(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    expected_operation: OperationWithMemoT,
) -> None:
    """Test that memo is NOT encrypted when it doesn't start with '#'."""
    node, _, pilot = prepared_tui_on_dashboard

    # ACT
    if isinstance(expected_operation, TransferOperation):
        await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
        await press_and_wait_for_screen(pilot, "enter", TransferToAccount)
        await fill_transfer_data(pilot, RECEIVER, AMOUNT, PLAIN_MEMO_CONTENT)
    else:
        await go_to_savings(pilot)
        await fill_savings_data(pilot, type(expected_operation), RECEIVER, AMOUNT, PLAIN_MEMO_CONTENT)

    log_current_view(pilot.app, nodes=True)

    await focus_next(pilot)  # Go to `Add to cart` button
    await process_operation(pilot, "FINALIZE_TRANSACTION")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


async def test_negative_transfer_encrypted_memo_without_memo_key(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """Test that error notification is shown when trying to encrypt memo without memo key imported."""
    node, wallet, pilot = prepared_tui_on_dashboard

    # ARRANGE - Change memo key to a new key that is not imported in beekeeper
    new_memo_key = PrivateKey.generate().calculate_public_key()
    current_key = tt.Account(WORKING_ACCOUNT_NAME).public_key
    wallet.api.update_account(
        WORKING_ACCOUNT_NAME,
        "{}",
        current_key,
        current_key,
        current_key,
        new_memo_key.value,
    )
    node.wait_number_of_blocks(1)

    # ACT
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    await fill_transfer_data(pilot, RECEIVER, AMOUNT, ENCRYPTED_MEMO_CONTENT)
    log_current_view(pilot.app, nodes=True)

    await focus_next(pilot)  # Go to `Add to cart` button
    await focus_next(pilot)  # Go to `Finalize transaction` button
    await pilot.press(CLIVE_PREDEFINED_BINDINGS.operations.finalize_transaction.key)
    await pilot.pause()

    # ASSERT - Should still be on TransferToAccount screen (operation was prevented)
    assert_is_screen_active(pilot, TransferToAccount)

    # Check that error notification was shown
    notifications = get_notification_messages(pilot)
    assert any(MEMO_KEY_NOT_IMPORTED_WARNING in msg for msg in notifications), (
        f"Expected notification about missing memo key, got: {notifications}"
    )


async def test_negative_transfer_encrypted_memo_to_nonexistent_account(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """Test that error notification is shown when trying to encrypt memo to a non-existent account."""
    _, _, pilot = prepared_tui_on_dashboard

    # ACT
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    await fill_transfer_data(pilot, NON_EXISTENT_ACCOUNT, AMOUNT, ENCRYPTED_MEMO_CONTENT)
    log_current_view(pilot.app, nodes=True)

    await focus_next(pilot)  # Go to `Add to cart` button
    await focus_next(pilot)  # Go to `Finalize transaction` button
    await pilot.press(CLIVE_PREDEFINED_BINDINGS.operations.finalize_transaction.key)
    await pilot.pause()

    # ASSERT - Should still be on TransferToAccount screen (operation was prevented)
    assert_is_screen_active(pilot, TransferToAccount)

    # Check that error notification was shown
    notifications = get_notification_messages(pilot)
    expected_message = f"Memo encryption failed: account '{NON_EXISTENT_ACCOUNT}' was not found."
    assert any(expected_message in msg for msg in notifications), (
        f"Expected notification about missing account, got: {notifications}"
    )


async def test_memo_encryption_indicator_shown_when_memo_starts_with_hash(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """Test that 'will be encrypted' indicator is shown when memo starts with '#'."""
    _, _, pilot = prepared_tui_on_dashboard

    # ACT
    await press_and_wait_for_screen(pilot, CLIVE_PREDEFINED_BINDINGS.dashboard.operations.key, Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    # Focus memo input
    await focus_next(pilot)  # From -> Amount
    await focus_next(pilot)  # Amount -> Asset select
    await focus_next(pilot)  # Asset select -> Memo

    # Get memo input widget
    memo_input = pilot.app.screen.query_one(MemoInput)

    # Initially, border_subtitle should be empty
    assert not memo_input.input.border_subtitle, "Border subtitle should be empty initially"

    # Type '#' to trigger encryption indicator
    await write_text(pilot, "#")
    await pilot.pause()

    # ASSERT - border_subtitle should show "will be encrypted"
    assert memo_input.input.border_subtitle == "will be encrypted", (  # type: ignore[comparison-overlap]
        f"Expected 'will be encrypted', got '{memo_input.input.border_subtitle}'"
    )

    # Type more text, indicator should still be shown
    await write_text(pilot, "secret message")
    await pilot.pause()

    assert memo_input.input.border_subtitle == "will be encrypted", (
        "Encryption indicator should persist while memo starts with '#'"
    )

    # Clear memo and type plain text
    for _ in range(len("#secret message")):
        await pilot.press("backspace")
    await pilot.pause()

    await write_text(pilot, "plain memo")
    await pilot.pause()

    # ASSERT - border_subtitle should be empty for plain memo
    assert not memo_input.input.border_subtitle, (
        f"Border subtitle should be empty for plain memo, got '{memo_input.input.border_subtitle}'"
    )
