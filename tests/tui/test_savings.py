from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt
from textual.widgets import RadioSet

from clive.__private.models.schemas import (
    CancelTransferFromSavingsOperation,
    TransferFromSavingsOperation,
    TransferToSavingsOperation,
)
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.operations import Operations
from clive.__private.ui.screens.operations.operation_summary.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.screens.operations.savings_operations.savings_operations import (
    PendingTransfer,
    Savings,
)
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.clive_basic import CliveRadioButton
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_DATA,
)
from clive_local_tools.tui.broadcast_transaction import broadcast_transaction
from clive_local_tools.tui.checkers import (
    assert_is_clive_composed_input_focused,
    assert_is_dashboard,
    assert_is_focused,
    assert_is_screen_active,
)
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    press_binding,
    write_text,
)
from clive_local_tools.tui.utils import log_current_view

if TYPE_CHECKING:
    from typing import Any

    from clive_local_tools.tui.types import ClivePilot, LiquidAssetToken, OperationProcessing


SENDER: Final[str] = WORKING_ACCOUNT_DATA.account.name
RECEIVER: Final[str] = WORKING_ACCOUNT_DATA.account.name
PASS: Final[str] = WORKING_ACCOUNT_DATA.account.name
OTHER_RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name


def is_to_savings_radio_button_checked(pilot: ClivePilot) -> bool:
    radio_buttons = pilot.app.query_one(CliveRadioButton)
    return radio_buttons.value


async def fill_savings_data(
    pilot: ClivePilot,
    operation_type: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
) -> None:
    """Assuming Savings is current screen."""
    assert_is_screen_active(pilot, Savings)
    amount = str(asset.as_float())
    asset_token: LiquidAssetToken = asset.token()  # type: ignore[assignment]
    await focus_next(pilot)  # Go to choose operation type
    assert_is_focused(pilot, RadioSet)
    if (operation_type is TransferToSavingsOperation) != is_to_savings_radio_button_checked(pilot):
        await pilot.press("right", "space")  # Mark the other option
    await focus_next(pilot)  # Go to choose beneficent account
    assert_is_clive_composed_input_focused(pilot, AccountNameInput)
    if other_account is not None:
        # clear currently introduced account name and input other_account
        await pilot.press("ctrl+w")
        await write_text(pilot, other_account)
    await focus_next(pilot)  # Go to amount input
    assert_is_clive_composed_input_focused(pilot, LiquidAssetAmountInput)
    await write_text(pilot, amount)
    await focus_next(pilot)  # Go to choose token
    assert_is_clive_composed_input_focused(pilot, LiquidAssetAmountInput, target="select")
    await choose_asset_token(pilot, asset_token)
    if memo:
        await focus_next(pilot)  # Go to choose memo
        assert_is_clive_composed_input_focused(pilot, MemoInput)
        await write_text(pilot, memo)


def prepare_expected_operation(
    operation_type: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
    request_id: int = 0,
) -> TransferFromSavingsOperation | TransferToSavingsOperation:
    data: dict[str, Any] = {
        "from_": SENDER,
        "to": other_account if other_account is not None else RECEIVER,
        "amount": asset,
        "memo": memo if memo else "",
    }

    if operation_type is TransferFromSavingsOperation:
        data["request_id"] = request_id

    return operation_type(**data)


async def go_to_savings(pilot: ClivePilot) -> None:
    assert_is_dashboard(pilot)
    await press_and_wait_for_screen(pilot, "f2", Operations)
    await focus_next(pilot)
    await focus_next(pilot)
    await press_and_wait_for_screen(pilot, "enter", Savings)


async def get_pending_transfers_from_savings_count(pilot: ClivePilot) -> int:
    await go_to_savings(pilot)
    assert_is_screen_active(pilot, Savings)
    pending_transfers = pilot.app.screen.query(PendingTransfer)
    tt.logger.debug(f"get_pending_transfers_from_savings_count: {len(pending_transfers)}")
    await press_and_wait_for_screen(pilot, "escape", Operations)
    await press_and_wait_for_screen(pilot, "escape", Dashboard)
    assert_is_dashboard(pilot)
    return len(pending_transfers)


async def assert_pending_transfers_from_savings_count(pilot: ClivePilot, expected_count: int) -> None:
    pending_transfers_from_savings_count = await get_pending_transfers_from_savings_count(pilot)
    assert pending_transfers_from_savings_count == expected_count, (
        f"Expected {expected_count} transfer(s)! Transfers' count: {pending_transfers_from_savings_count}"
        if expected_count > 0
        else "Expected no pending transfers!"
    )


TESTDATA: Final[list[tuple[str | None, OperationProcessing]]] = [
    (None, "FINALIZE_TRANSACTION"),
    ("memo2", "ADD_TO_CART"),
]


@pytest.mark.parametrize(("memo", "operation_processing"), TESTDATA)
@pytest.mark.parametrize("asset", [tt.Asset.Hive(3.14), tt.Asset.Hbd(2.7)])
@pytest.mark.parametrize("other_account", [None, OTHER_RECEIVER])
@pytest.mark.parametrize("operation_type", [TransferFromSavingsOperation, TransferToSavingsOperation])
async def test_savings(  # noqa: PLR0913
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_type: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
    operation_processing: OperationProcessing,
) -> None:
    """
    #110: I-II (create transfer to/from savings).

    1. The user an operation in HBD/HIVE without memo (if possible) to own account/another account and finalizes
       transaction.
    2. The user an operation in HBD/HIVE to own account/another account, adds to the cart and then broadcasts it.
    """
    node, _, pilot = prepared_tui_on_dashboard

    # ARRANGE
    expected_operation = prepare_expected_operation(
        operation_type, other_account, asset, memo, 0 + WORKING_ACCOUNT_DATA.from_savings_transfer_count
    )

    # TODO: save balances before transfer

    # ACT
    ### Create transfer to savings
    await go_to_savings(pilot)
    await pilot.press("right")

    # Fill transfer to savings data
    await fill_savings_data(pilot, operation_type, other_account, asset, memo)
    log_current_view(pilot.app, nodes=True)

    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)

    if operation_type is TransferFromSavingsOperation:
        await assert_pending_transfers_from_savings_count(pilot, 1 + WORKING_ACCOUNT_DATA.from_savings_transfer_count)
        # TODO: check if pending transfer is as expected_operation


TRANSFERS_DATA: Final[list[tuple[tt.Asset.HbdT | tt.Asset.HiveT, str]]] = [
    (tt.Asset.Hbd("2.0"), "memo0"),
    (tt.Asset.Hive("2.1"), "memo1"),
]
TRANSFERS_COUNT: Final[int] = len(TRANSFERS_DATA)


@pytest.mark.parametrize("other_account", [None, OTHER_RECEIVER])
@pytest.mark.parametrize("operation_type", [TransferFromSavingsOperation, TransferToSavingsOperation])
async def test_savings_finalize_cart(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_type: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
) -> None:
    """
    #110: I-II (create transfer to/from savings).

    4. The user makes two operations to own account/another account, the first in HBD, the second in HIVE,
       adds them to cart and then broadcasts.
    """
    node, _, pilot = prepared_tui_on_dashboard

    # ARRANGE
    expected_operations = [
        prepare_expected_operation(
            operation_type,
            other_account,
            TRANSFERS_DATA[i][0],
            TRANSFERS_DATA[i][1],
            i + WORKING_ACCOUNT_DATA.from_savings_transfer_count,
        )
        for i in range(TRANSFERS_COUNT)
    ]

    # TODO: save balances before transfer

    # ACT
    ### Create transfers
    # Choose savings operation
    await go_to_savings(pilot)
    await pilot.press("right")

    for i in range(TRANSFERS_COUNT):
        # Fill transfer savings data
        log_current_view(pilot.app, nodes=True, source=f"before fill_savings_data({i})")
        await fill_savings_data(pilot, operation_type, other_account, TRANSFERS_DATA[i][0], TRANSFERS_DATA[i][1])
        log_current_view(pilot.app, nodes=True, source=f"after fill_savings_data({i})")

        await focus_next(pilot)  # focus add to cart button
        await press_binding(pilot, "f2", "Add to cart")
        await focus_next(pilot)  # focus transfer tab pane
        log_current_view(pilot.app)

    await press_and_wait_for_screen(pilot, "escape", Operations)
    await press_and_wait_for_screen(pilot, "f2", TransactionSummary)  # Go to transaction summary
    await broadcast_transaction(pilot)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)

    if operation_type is TransferFromSavingsOperation:
        assert_is_dashboard(pilot)
        await assert_pending_transfers_from_savings_count(
            pilot, TRANSFERS_COUNT + WORKING_ACCOUNT_DATA.from_savings_transfer_count
        )
        # TODO: check if pending transfers in TUI are as expected_operation


async def test_canceling_transfer_from_savings(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """#110: III (cancel transfer from savings)."""
    node, wallet, pilot = prepared_tui_on_dashboard

    # ARRANGE
    expected_operations = [
        CancelTransferFromSavingsOperation(from_=SENDER, request_id=i) for i in range(TRANSFERS_COUNT)
    ]

    for i in range(TRANSFERS_COUNT):
        wallet.api.transfer_from_savings(
            SENDER,
            i + WORKING_ACCOUNT_DATA.from_savings_transfer_count,
            RECEIVER,
            TRANSFERS_DATA[i][0].as_nai(),
            TRANSFERS_DATA[i][1],
        )

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # TODO: check if pending transfers are as expected in TUI

    for i in range(TRANSFERS_COUNT):
        # ASSERT
        await assert_pending_transfers_from_savings_count(
            pilot, TRANSFERS_COUNT - i + WORKING_ACCOUNT_DATA.from_savings_transfer_count
        )

        # Test canceling first transfer from savings
        # ACT
        await go_to_savings(pilot)
        await focus_next(pilot)
        await press_and_wait_for_screen(pilot, "enter", CancelTransferFromSavings)  # Cancel transfer
        await press_and_wait_for_screen(pilot, "f6", TransactionSummary)  # Finalize transaction
        await broadcast_transaction(pilot)

        transaction_id = await extract_transaction_id_from_notification(pilot)

        # ASSERT
        assert_operations_placed_in_blockchain(node, transaction_id, expected_operations[i])

    # ASSERT
    await assert_pending_transfers_from_savings_count(pilot, WORKING_ACCOUNT_DATA.from_savings_transfer_count)
