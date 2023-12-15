from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.operations.savings_operations.savings_operations import PendingTransfer, Savings
from clive_local_tools.tui.activate import activate
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT
from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual import get_notification_transaction_id, is_key_binding_active, write_text
from clive_local_tools.tui.utils import (
    assert_operations_placed_in_blockchain,
    get_mode,
    get_profile_name,
    log_current_view,
)
from schemas.operations import TransferFromSavingsOperation, TransferToSavingsOperation

if TYPE_CHECKING:
    from typing import Any

    from textual.pilot import Pilot

    from clive_local_tools.tui.types import OPERATION_PROCESSING


SENDER: Final[str] = WORKING_ACCOUNT.name
RECEIVER: Final[str] = WORKING_ACCOUNT.name
PASS: Final[str] = WORKING_ACCOUNT.name
OTHER_RECEIVER: Final[str] = WATCHED_ACCOUNTS[0].name


async def fill_savings_data(
    pilot: Pilot[int],
    mode: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
) -> None:
    """Assuming Savings is current screen."""
    assert isinstance(
        pilot.app.screen, Savings
    ), f"'create_savings' requires 'Savings' to be the current screen! Current screen is: '{pilot.app.screen}'."
    asset_token: str = asset.token()
    amount: str = str(asset.as_float())
    await pilot.press("tab")
    if mode is TransferFromSavingsOperation:
        await pilot.press("right", "space")  # mark 'transfer from savings'
    await pilot.press("tab")
    if other_account:
        # clear existing account name and input other_account
        await pilot.press("ctrl+w")
        await write_text(pilot, other_account)
    await pilot.press("tab")
    await write_text(pilot, amount)
    await pilot.press("tab")
    await choose_asset_token(pilot, asset_token)
    if memo:
        await pilot.press("tab")
        await write_text(pilot, memo)


def prepare_expected_operation(
    mode: type[TransferFromSavingsOperation | TransferToSavingsOperation],
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

    if mode is TransferFromSavingsOperation:
        data["request_id"] = request_id

    return mode(**data)


TESTDATA: Final[list[tuple[str | None, OPERATION_PROCESSING]]] = [
    ("memo1", "FAST_BROADCAST"),
    (None, "FINALIZE_TRANSACTION"),
    ("memo2", "ADD_TO_CART"),
]


@pytest.mark.parametrize(("memo", "operation_processing"), TESTDATA)
@pytest.mark.parametrize("asset", [tt.Asset.Hive(3.14), tt.Asset.Hbd(2.7)])
@pytest.mark.parametrize("other_account", [None, OTHER_RECEIVER])
@pytest.mark.parametrize("mode", [TransferFromSavingsOperation, TransferToSavingsOperation])
@pytest.mark.parametrize("activated", [True, False])
async def test_savings(  # noqa: PLR0913
    prepared_tui_on_dashboard: tuple[tt.InitNode, Pilot[int]],
    activated: bool,
    mode: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
    asset: tt.Asset.HbdT | tt.Asset.HiveT,
    memo: str | None,
    operation_processing: OPERATION_PROCESSING,
) -> None:
    """
    #110: I-IV (create transfer to/from savings) and V-VI (cancel transfer from savings).

    Clive is activated/deactivated. Then:
    1. The user an operation in HBD/HIVE with memo (if possible) to own account/another account and fast broadcasts it.
    2. The user an operation in HBD/HIVE without memo (if possible) to own account/another account and finalizes transaction.
    3. The user an operation in HBD/HIVE to own account/another account, adds to the cart and then broadcasts it.
    """
    node, pilot = prepared_tui_on_dashboard

    # ARRANGE
    log_current_view(pilot.app, nodes=True)
    tt.logger.debug(f"profile name: '{get_profile_name(pilot.app)}'")
    assert get_mode(pilot.app) == "inactive", "Expected 'inactive' mode!"

    expected = prepare_expected_operation(mode, other_account, asset, memo)

    # TODO: save balances before transfer
    ...

    # ACT
    if activated:
        await activate(pilot, PASS)

    ### Create transfer to savings
    # Go to savings operation
    await pilot.press("f2", "tab", "tab", "enter", "right")

    # Fill transfer to savings data
    await fill_savings_data(pilot, mode, other_account, asset, memo)
    log_current_view(pilot.app, nodes=True)

    await process_operation(pilot, operation_processing, activated, PASS)

    transaction_id = await get_notification_transaction_id(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected)

    if mode is TransferFromSavingsOperation:
        log_current_view(pilot.app, nodes=True)
        if isinstance(pilot.app.screen, Operations):
            tt.logger.debug(f"is_key_binding_active('esc'): {is_key_binding_active(pilot.app, 'esc', 'Back')}")
            await pilot.press("enter")  # assuming focus on 'Savings' button
        else:
            await pilot.press("f2", "tab", "tab", "enter")  # go to savings
        log_current_view(pilot.app, nodes=True)
        pending_transfer = pilot.app.query(PendingTransfer)
        assert len(pending_transfer) == 1, f"Expected 1 transfer! Transfers' count: {len(pending_transfer)}"

        # test canceling transfer from savings
        # ACT
        await pilot.press("tab", "enter")  # Cancel transfer

        # ASSERT
        await pilot.press("enter")  # go to savings
        pending_transfer = pilot.app.query(PendingTransfer)
        assert len(pending_transfer) == 0, "Expected no pending transfers!"


ASSETS: Final[list[tt.Asset.HbdT | tt.Asset.HiveT]] = [
    tt.Asset.Hbd("2.0"),
    tt.Asset.Hive("2.1"),
]
MEMOS: Final[list[str]] = [
    "memo0",
    "memo1",
]


@pytest.mark.parametrize("other_account", [None, OTHER_RECEIVER])
@pytest.mark.parametrize("mode", [TransferFromSavingsOperation, TransferToSavingsOperation])
@pytest.mark.parametrize("activated", [True, False])
async def test_cancel_transfers_from_savings(
    prepared_tui_on_dashboard: tuple[tt.InitNode, Pilot[int]],
    activated: bool,
    mode: type[TransferFromSavingsOperation | TransferToSavingsOperation],
    other_account: str | None,  # None means using current profile account name
) -> None:
    """
    #110: I-IV (create transfer to/from savings) and V-VI (cancel transfer from savings).

    Clive is activated/deactivated. Then:
    4. The user makes two operations to own account/another account, the first in HBD, the second in HIVE,
       adds them to cart and then broadcasts.
    """
    node, pilot = prepared_tui_on_dashboard

    # ARRANGE
    log_current_view(pilot.app, nodes=True)
    tt.logger.debug(f"profile name: '{get_profile_name(pilot.app)}'")
    assert get_mode(pilot.app) == "inactive", "Expected 'inactive' mode!"

    expected0 = prepare_expected_operation(mode, other_account, ASSETS[0], MEMOS[0], 0)
    expected1 = prepare_expected_operation(mode, other_account, ASSETS[1], MEMOS[1], 1)

    # TODO: save balances before transfer
    ...

    # ACT
    if activated:
        await activate(pilot, PASS)

    ### Create 2 transfers
    # Choose savings operation
    await pilot.press("f2", "tab", "tab")

    for i in range(2):
        # Fill transfer to savings data
        await pilot.press("enter", "right")  # go to savings operation
        await fill_savings_data(pilot, mode, other_account, ASSETS[i], MEMOS[i])
        log_current_view(pilot.app, nodes=True)

        await pilot.press("f2")  # add to cart (goes back to Operations screen)
        log_current_view(pilot.app)

    await pilot.press("f2")  # go to cart
    await finalize_transaction(pilot, activated, PASS)

    transaction_id = await get_notification_transaction_id(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected0, expected1)

    if mode is TransferFromSavingsOperation:
        await pilot.press("f2", "tab", "tab", "enter")  # go to savings
        log_current_view(pilot.app, nodes=True)
        pending_transfer = pilot.app.query(PendingTransfer)
        assert (
            len(pending_transfer) == 2  # noqa: PLR2004
        ), f"Expected 2 transfers! Transfers' count: {len(pending_transfer)}"

        # Test canceling first transfer from savings
        # ACT
        """
        if activated is False:
            await pilot.press("esc", "esc")  # go to dashboard
            await pilot.press("f4")  # deactivate before cancel transfer
            await pilot.press("f2", "tab", "tab", "enter")  # go to savings
        """

        await pilot.press("tab", "enter")  # Cancel transfer
        # await fast_broadcast(pilot, activated, PASS)  # noqa: ERA001
        await fast_broadcast(pilot, True)  # already activated

        # ASSERT
        await pilot.press("enter")  # go to savings
        log_current_view(pilot.app, nodes=True)
        pending_transfer = pilot.app.query(PendingTransfer)
        assert len(pending_transfer) == 1, f"Expected 1 transfer! Transfers' count: {len(pending_transfer)}"

        # Test canceling second transfer from savings
        # ACT
        """
        if activated is False:
            await pilot.press("esc", "esc")  # go to dashboard
            await pilot.press("f4")  # deactivate before cancel transfer
            await pilot.press("f2", "tab", "tab", "enter")  # go to savings
        """

        await pilot.press("tab", "enter")  # Cancel transfer
        # await finalize_transaction(pilot, activated, PASS)  # noqa: ERA001
        await finalize_transaction(pilot, True)  # already activated

        # ASSERT
        await pilot.press("f2", "tab", "tab", "enter")  # go to savings
        log_current_view(pilot.app, nodes=True)
        pending_transfer = pilot.app.query(PendingTransfer)
        assert len(pending_transfer) == 0, "Expected no pending transfers!"
