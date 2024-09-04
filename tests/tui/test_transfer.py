from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.models.schemas import TransferOperation
from clive.__private.ui.screens.operations import Operations, TransferToAccount
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.__private.ui.widgets.inputs.memo_input import MemoInput
from clive_local_tools.checkers import assert_operations_placed_in_blockchain
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA
from clive_local_tools.tui.checkers import assert_is_clive_composed_input_focused, assert_is_screen_active
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    write_text,
)
from clive_local_tools.tui.unlock import unlock
from clive_local_tools.tui.utils import is_header_in_locked_mode, log_current_view

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
    ("memo1", "FAST_BROADCAST"),
    (None, "FINALIZE_TRANSACTION"),
    ("memo2", "ADD_TO_CART"),
]


@pytest.mark.parametrize("unlocked", ["True", "False"])
@pytest.mark.parametrize("asset", [tt.Asset.Hive(1.03), tt.Asset.Hbd(2)])
@pytest.mark.parametrize(("memo", "operation_processing"), TESTDATA)
async def test_transfers(
    prepared_tui_on_dashboard_locked: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
    operation_processing: OperationProcessing,
    *,
    unlocked: bool,
) -> None:
    """
    #103: I.1..3, II.1..3.

    Clive in unlocked/locked modes. Then:
    1. The user makes a transfer in HBD/HIVE with memo and Fast broadcasts it.
    2. The user makes a transfer in HBD/HIVE without memo and finalizes transaction.
    3. The user makes a transfer in HBD/HIVE, adds to the cart and then broadcasts it.
    """
    node, _, pilot = prepared_tui_on_dashboard_locked

    # ARRANGE
    log_current_view(pilot.app, nodes=True)
    assert is_header_in_locked_mode(pilot.app), "Expected locked mode!"

    expected_operation = TransferOperation(
        from_=SENDER,
        to=RECEIVER,
        amount=asset,
        memo=memo if memo else "",
    )

    # TODO: save balances before transfer

    # ACT
    if unlocked:
        await unlock(pilot, PASS)

    ### Create transfer
    await press_and_wait_for_screen(pilot, "f2", Operations)
    await focus_next(pilot)  # Choose transfer operation
    await press_and_wait_for_screen(pilot, "enter", TransferToAccount)

    # Fill transfer data
    await fill_transfer_data(pilot, RECEIVER, asset, memo)
    log_current_view(pilot.app, nodes=True)

    await process_operation(pilot, operation_processing, unlocked=unlocked)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    log_current_view(pilot.app)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


TRANSFERS_DATA: Final[list[tuple[tt.Asset.HbdT | tt.Asset.HiveT, str]]] = [
    (tt.Asset.Hbd("1.0"), "memo0"),
    (tt.Asset.Hive("1.1"), "memo1"),
]
TRANSFERS_COUNT: Final[int] = len(TRANSFERS_DATA)


@pytest.mark.parametrize("unlocked", [True, False])
async def test_transfers_finalize_cart(
    prepared_tui_on_dashboard_locked: tuple[tt.RawNode, tt.Wallet, ClivePilot], *, unlocked: bool
) -> None:
    """
    #103: I.4, II.4.

    Clive in unlocked/locked modes. Then:
    4. The user makes two transfers, the first in HBD, the second in HIVE, adds them to cart and then broadcasts.
    """
    node, _, pilot = prepared_tui_on_dashboard_locked

    # ARRANGE
    log_current_view(pilot.app, nodes=True)
    assert is_header_in_locked_mode(pilot.app), "Expected locked mode!"

    expected_operations = [
        TransferOperation(from_=SENDER, to=RECEIVER, amount=TRANSFERS_DATA[i][0], memo=TRANSFERS_DATA[i][1])
        for i in range(TRANSFERS_COUNT)
    ]

    # TODO: save balances before transfer

    # ACT
    if unlocked:
        await unlock(pilot, PASS)

    ### Create 2 transfers
    # Choose transfer operation
    await press_and_wait_for_screen(pilot, "f2", Operations)
    await focus_next(pilot)

    for i in range(TRANSFERS_COUNT):
        # Fill transfer data
        await press_and_wait_for_screen(pilot, "enter", TransferToAccount)
        await fill_transfer_data(pilot, RECEIVER, TRANSFERS_DATA[i][0], TRANSFERS_DATA[i][1])
        log_current_view(pilot.app, nodes=True)

        await press_and_wait_for_screen(pilot, "f2", Operations)  # Add to cart
        log_current_view(pilot.app)

    await press_and_wait_for_screen(pilot, "f2", TransactionSummary)  # Go to transaction summary
    await finalize_transaction(pilot, unlocked=unlocked, password=PASS)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)
