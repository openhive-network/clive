from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt
from textual.widgets import RadioSet

from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.operation_summary.cancel_transfer_from_savings import CancelTransferFromSavings
from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.operations.savings_operations.savings_operations import (
    PendingTransfer,
    Savings,
)
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS,
    WORKING_ACCOUNT,
    WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT,
)
from clive_local_tools.tui.checkers import (
    assert_is_clive_composed_input_focused,
    assert_is_focused,
    assert_is_screen_active,
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    write_text,
)
from clive_local_tools.tui.utils import log_current_view
from schemas.operations import (
    CancelTransferFromSavingsOperation,
    TransferFromSavingsOperation,
    TransferToSavingsOperation,
)

if TYPE_CHECKING:
    from typing import Any

    from clive_local_tools.tui.types import ClivePilot, LiquidAssetToken, OperationProcessing


SENDER: Final[str] = WORKING_ACCOUNT.name
RECEIVER: Final[str] = WORKING_ACCOUNT.name
PASS: Final[str] = WORKING_ACCOUNT.name
OTHER_RECEIVER: Final[str] = WATCHED_ACCOUNTS[0].name


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
    if operation_type is TransferFromSavingsOperation:
        await pilot.press("right", "space")  # Mark 'transfer from savings'
    await focus_next(pilot)  # Go to choose beneficient account
    assert_is_clive_composed_input_focused(pilot, AccountNameInput)
    if other_account is not None:
        # clear currently introduced account name and input other_account
        await pilot.press("ctrl+w")
        await write_text(pilot, other_account)
    await focus_next(pilot)
    assert_is_clive_composed_input_focused(pilot, AccountNameInput, target="known")
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
    assert_is_screen_active(pilot, DashboardActive)
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
    await press_and_wait_for_screen(pilot, "escape", DashboardActive)
    return len(pending_transfers)


async def assert_pending_transfers_from_savings_count(pilot: ClivePilot, expected_count: int) -> None:
    pending_transfers_from_savings_count = await get_pending_transfers_from_savings_count(pilot)
    assert pending_transfers_from_savings_count == expected_count, (
        f"Expected {expected_count} transfer(s)! Transfers' count: {pending_transfers_from_savings_count}"
        if expected_count > 0
        else "Expected no pending transfers!"
    )


TESTDATA: Final[list[tuple[str | None, OperationProcessing]]] = [
    ("memo1", "FAST_BROADCAST"),
    (None, "FINALIZE_TRANSACTION"),
    ("memo2", "ADD_TO_CART"),
]


@pytest.mark.parametrize(("memo", "operation_processing"), TESTDATA)
@pytest.mark.parametrize("asset", [tt.Asset.Hive(3.14), tt.Asset.Hbd(2.7)])
@pytest.mark.parametrize("other_account", [None, OTHER_RECEIVER])
@pytest.mark.parametrize("operation_type", [TransferFromSavingsOperation, TransferToSavingsOperation])
async def test_savings(  # noqa: PLR0913
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_type: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
    operation_processing: OperationProcessing,
) -> None:
    """
    #110: I-II (create transfer to/from savings).

    Clive is activated. Then:
    1. The user an operation in HBD/HIVE with memo (if possible) to own account/another account and Fast broadcasts it.
    2. The user an operation in HBD/HIVE without memo (if possible) to own account/another account and finalizes transaction.
    3. The user an operation in HBD/HIVE to own account/another account, adds to the cart and then broadcasts it.
    """
    node, _, pilot = prepared_tui_on_dashboard_active

    # ARRANGE
    expected_operation = prepare_expected_operation(
        operation_type, other_account, asset, memo, 0 + WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT
    )

    # TODO: save balances before transfer

    # ACT
    ### Create transfer to savings
    await go_to_savings(pilot)
    await pilot.press("right")

    # Fill transfer to savings data
    await fill_savings_data(pilot, operation_type, other_account, asset, memo)
    log_current_view(pilot.app, nodes=True)

    await process_operation(pilot, operation_processing, True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)

    if operation_type is TransferFromSavingsOperation:
        if operation_processing == "FAST_BROADCAST":
            await press_and_wait_for_screen(pilot, "escape", DashboardActive)
        await assert_pending_transfers_from_savings_count(pilot, 1 + WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT)
        # TODO: check if pending transfer is as expected_operation


TRANSFERS_DATA: Final[list[tuple[tt.Asset.HbdT | tt.Asset.HiveT, str]]] = [
    (tt.Asset.Hbd("2.0"), "memo0"),
    (tt.Asset.Hive("2.1"), "memo1"),
]
TRANSFERS_COUNT: Final[int] = len(TRANSFERS_DATA)


@pytest.mark.parametrize("other_account", [None, OTHER_RECEIVER])
@pytest.mark.parametrize("operation_type", [TransferFromSavingsOperation, TransferToSavingsOperation])
async def test_savings_finalize_cart(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_type: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
) -> None:
    """
    #110: I-II (create transfer to/from savings).

    Clive is activated. Then:
    4. The user makes two operations to own account/another account, the first in HBD, the second in HIVE, adds them to cart and then broadcasts.
    """
    node, _, pilot = prepared_tui_on_dashboard_active

    # ARRANGE
    expected_operations = [
        prepare_expected_operation(
            operation_type,
            other_account,
            TRANSFERS_DATA[i][0],
            TRANSFERS_DATA[i][1],
            i + WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT,
        )
        for i in range(TRANSFERS_COUNT)
    ]

    # TODO: save balances before transfer

    # ACT
    ### Create transfers
    # Choose savings operation
    for i in range(TRANSFERS_COUNT):
        # Fill transfer savings data
        await go_to_savings(pilot)
        await pilot.press("right")
        log_current_view(pilot.app, nodes=True, source=f"before fill_savings_data({i})")
        await fill_savings_data(pilot, operation_type, other_account, TRANSFERS_DATA[i][0], TRANSFERS_DATA[i][1])
        log_current_view(pilot.app, nodes=True, source=f"after fill_savings_data({i})")

        await press_and_wait_for_screen(pilot, "f2", Operations)  # Add to cart
        await press_and_wait_for_screen(pilot, "escape", DashboardActive)
        log_current_view(pilot.app)

    await press_and_wait_for_screen(pilot, "f2", Operations)  # Go to Operations
    await press_and_wait_for_screen(pilot, "f2", Cart)  # Go to Cart
    await finalize_transaction(pilot, True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)

    if operation_type is TransferFromSavingsOperation:
        assert_is_screen_active(pilot, DashboardActive)
        await assert_pending_transfers_from_savings_count(
            pilot, TRANSFERS_COUNT + WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT
        )
        # TODO: check if pending transfers in TUI are as expected_operation


async def test_canceling_transfer_from_savings(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """#110: III (cancel transfer from savings)."""
    node, wallet, pilot = prepared_tui_on_dashboard_active

    # ARRANGE
    expected_operations = [
        CancelTransferFromSavingsOperation(from_=SENDER, request_id=i) for i in range(TRANSFERS_COUNT)
    ]

    for i in range(TRANSFERS_COUNT):
        wallet.api.transfer_from_savings(
            SENDER,
            i + WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT,
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
            pilot, TRANSFERS_COUNT - i + WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT
        )

        # Test canceling first transfer from savings
        # ACT
        await go_to_savings(pilot)
        await focus_next(pilot)
        await press_and_wait_for_screen(pilot, "enter", CancelTransferFromSavings)  # Cancel transfer
        await fast_broadcast(pilot, True)
        await press_and_wait_for_screen(pilot, "escape", DashboardActive)

        transaction_id = await extract_transaction_id_from_notification(pilot)

        # Wait for transaction be available in block
        node.wait_number_of_blocks(1)

        # ASSERT
        assert_operations_placed_in_blockchain(node, transaction_id, expected_operations[i])

    # ASSERT
    await assert_pending_transfers_from_savings_count(pilot, WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT)
