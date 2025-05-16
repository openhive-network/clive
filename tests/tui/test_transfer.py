from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.constants.tui.operations_common_bindings import ADD_OPERATION_TO_CART
from clive.__private.models.schemas import TransferOperation
from clive.__private.ui.screens.operations import Operations, TransferToAccount
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA
from clive_local_tools.tui.broadcast_transaction import broadcast_transaction
from clive_local_tools.tui.checkers import assert_is_clive_composed_input_focused, assert_is_screen_active
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
    from clive_local_tools.tui.types import ClivePilot, LiquidAssetToken, OperationProcessing


SENDER: Final[str] = WORKING_ACCOUNT_DATA.account.name
PASS: Final[str] = WORKING_ACCOUNT_DATA.account.name
RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name


async def fill_transfer_data(
    pilot: ClivePilot, beneficient: str, asset: tt.Asset.HbdT | tt.Asset.HiveT, memo: str | None
) -> None:
    """Assuming Transfer is current screen."""
    assert_is_screen_active(pilot, TransferToAccount)
    amount = str(asset.as_float())
    asset_token: LiquidAssetToken = asset.token()  # type: ignore[assignment]
    assert_is_clive_composed_input_focused(
        pilot, AccountNameInput, context="TransferToAccount should have initial focus"
    )
    await write_text(pilot, beneficient)
    await focus_next(pilot)
    assert_is_clive_composed_input_focused(pilot, LiquidAssetAmountInput)
    await write_text(pilot, amount)
    await focus_next(pilot)
    assert_is_clive_composed_input_focused(pilot, LiquidAssetAmountInput, target="select")
    await choose_asset_token(pilot, asset_token)
    if memo:
        await focus_next(pilot)
        assert_is_clive_composed_input_focused(pilot, MemoInput)
        await write_text(pilot, memo)


TESTDATA: Final[list[tuple[str | None, OperationProcessing]]] = [
    (None, "FINALIZE_TRANSACTION"),
    ("memo2", "ADD_TO_CART"),
]


@pytest.mark.parametrize("asset", [tt.Asset.Hive(1.03), tt.Asset.Hbd(2)])
@pytest.mark.parametrize(("memo", "operation_processing"), TESTDATA)
async def test_transfers(
    prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
    operation_processing: OperationProcessing,
) -> None:
    """
    #103: I.2..3, II.2..3.

    1. The user makes a transfer in HBD/HIVE without memo and finalizes transaction.
    2. The user makes a transfer in HBD/HIVE, adds to the cart and then broadcasts it.
    """
    node, _, pilot = prepared_tui_on_dashboard

    # ARRANGE
    log_current_view(pilot.app, nodes=True)

    expected_operation = TransferOperation(
        from_=SENDER,
        to=RECEIVER,
        amount=asset,
        memo=memo if memo else "",
    )

    # TODO: save balances before transfer

    # ACT
    ### Create transfer
    await press_and_wait_for_screen(pilot, "f2", Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    # Fill transfer data
    await fill_transfer_data(pilot, RECEIVER, asset, memo)
    log_current_view(pilot.app, nodes=True)

    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    log_current_view(pilot.app)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


TRANSFERS_DATA: Final[list[tuple[tt.Asset.HbdT | tt.Asset.HiveT, str]]] = [
    (tt.Asset.Hbd("1.0"), "memo0"),
    (tt.Asset.Hive("1.1"), "memo1"),
]
TRANSFERS_COUNT: Final[int] = len(TRANSFERS_DATA)


async def test_transfers_finalize_cart(prepared_tui_on_dashboard: tuple[tt.RawNode, tt.Wallet, ClivePilot]) -> None:
    """
    #103: I.4, II.4.

    4. The user makes two transfers, the first in HBD, the second in HIVE, adds them to cart and then broadcasts.
    """
    node, _, pilot = prepared_tui_on_dashboard

    # ARRANGE
    log_current_view(pilot.app, nodes=True)

    expected_operations = [
        TransferOperation(from_=SENDER, to=RECEIVER, amount=TRANSFERS_DATA[i][0], memo=TRANSFERS_DATA[i][1])
        for i in range(TRANSFERS_COUNT)
    ]

    # TODO: save balances before transfer

    # ACT
    ### Create 2 transfers
    # Choose transfer operation
    await press_and_wait_for_screen(pilot, "f2", Operations)
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    for i in range(TRANSFERS_COUNT):
        # Fill transfer data
        await fill_transfer_data(pilot, RECEIVER, TRANSFERS_DATA[i][0], TRANSFERS_DATA[i][1])
        log_current_view(pilot.app, nodes=True)
        await focus_next(pilot)  # focus on add to cart button
        await focus_next(pilot)  # focus on finalize transaction button
        await focus_next(pilot)  # focus on "to" input
        await press_binding(pilot, ADD_OPERATION_TO_CART.key, "Add to cart")
        log_current_view(pilot.app)

    await press_and_wait_for_screen(pilot, "escape", Operations)
    await press_and_wait_for_screen(pilot, "f2", TransactionSummary)  # Go to transaction summary
    await broadcast_transaction(pilot)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)
