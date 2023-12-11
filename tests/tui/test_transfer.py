from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.ui.operations.transfer_to_account.transfer_to_account import TransferToAccount
from clive.models import Asset
from clive_local_tools.tui.activate import activate
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT
from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.textual import get_notification_transaction_id, write_text
from clive_local_tools.tui.utils import get_mode, log_current_view
from schemas.operations import TransferOperation

if TYPE_CHECKING:
    from textual.pilot import Pilot

    from clive_local_tools.tui.types import ASSET_TOKEN, OPERATION_PROCESSING


USER: Final[str] = WORKING_ACCOUNT.name
PASS: Final[str] = WORKING_ACCOUNT.name
USER1: Final[str] = WATCHED_ACCOUNTS[0].name
AMOUNT: Final[str] = "1.03"


async def fill_transfer_data(
    pilot: Pilot[int], beneficient: str, amount: str, asset_token: ASSET_TOKEN, memo: str | None
) -> None:
    """Assuming Transfer is current screen."""
    assert isinstance(pilot.app.screen, TransferToAccount), (
        "'fill_transfer_data' requires 'TransferToAccount' to be the current screen! Current screen is:"
        f" '{pilot.app.screen}'."
    )
    await write_text(pilot, beneficient)
    await pilot.press("tab", "tab")
    await write_text(pilot, amount)
    await pilot.press("tab")
    await choose_asset_token(pilot, asset_token)
    if memo:
        await pilot.press("tab")
        await write_text(pilot, memo)


testdata = [
    ("memo1", "FAST_BROADCAST"),
    (None, "FINALIZE_TRANSACTION"),
    ("memo2", "ADD_TO_CART"),
]


@pytest.mark.parametrize("activated", ["True", "False"])
@pytest.mark.parametrize("asset_token", ["HIVE", "HBD"])
@pytest.mark.parametrize(("memo", "operation_processing"), testdata)
async def test_transfers(
    prepared_tui_on_dashboard: tuple[tt.InitNode, Pilot[int]],
    activated: bool,
    asset_token: ASSET_TOKEN,
    memo: str | None,
    operation_processing: OPERATION_PROCESSING,
) -> None:
    """
    #103: I.1..3, II.1..3.

    Clive in activated/deactivated modes. Then:
    1. The user makes a transfer in HBD/HIVE with memo and Fast broadcasts it.
    2. The user makes a transfer in HBD/HIVE without memo and finalizes transaction.
    3. The user makes a transfer in HBD/HIVE, adds to the cart and then broadcasts it.
    """
    node, pilot = prepared_tui_on_dashboard

    # ARRANGE
    log_current_view(pilot.app, nodes=True)
    assert get_mode(pilot.app) == "inactive", "Expected 'inactive' mode!"

    if activated:
        await activate(pilot, PASS)

    expected = TransferOperation(
        from_=USER,
        to=USER1,
        amount=Asset.hive(AMOUNT) if asset_token == "HIVE" else Asset.hbd(AMOUNT),
        memo=memo if memo else "",
    )

    # TODO: save balances before transfer
    ...

    # ACT
    ### Create transfer
    # Choose transfer operation
    await pilot.press("f2", "tab", "enter")
    # Fill transfer data
    await fill_transfer_data(pilot, USER1, AMOUNT, asset_token, memo)
    log_current_view(pilot.app, nodes=True)

    if operation_processing == "FAST_BROADCAST":
        await fast_broadcast(pilot, activated, PASS)
    else:  # "ADD_TO_CART" or "FINALIZE_TRANSACTION"
        if operation_processing == "ADD_TO_CART":
            await pilot.press("f2", "f2")  # add to cart, go to cart
        await finalize_transaction(pilot, activated, PASS)

    await get_notification_transaction_id(pilot)

    log_current_view(pilot.app)

    node.wait_number_of_blocks(1)

    # ASSERT
    history = node.api.account_history.get_account_history(account=USER, include_reversible=True)["history"]
    operation = history[-1][1]["op"]
    tt.logger.debug(f"operation: {operation}")
    assert (
        operation["type"] == "transfer_operation"
    ), f"Expected 'transfer_operation' type! Current is '{operation['type']}'"
    assert operation["value"] == expected.dict(by_alias=True), "Transfer operation different than expected!"


@pytest.mark.parametrize("activated", [True, False])
async def test_transfers_finalize_cart(
    prepared_tui_on_dashboard: tuple[tt.InitNode, Pilot[int]], activated: bool
) -> None:
    """
    #103: I.4, II.4.

    Clive in activated/deactivated modes. Then:
    4. The user makes two transfers, the first in HBD, the second in HIVE, adds them to cart and then broadcasts.
    """
    node, pilot = prepared_tui_on_dashboard

    # ARRANGE
    log_current_view(pilot.app, nodes=True)
    assert get_mode(pilot.app) == "inactive", "Expected 'inactive' mode!"

    if activated:
        await activate(pilot, PASS)

    expected0 = TransferOperation(from_=USER, to=USER1, amount=Asset.hbd("1.0"), memo="memo0")

    expected1 = TransferOperation(from_=USER, to=USER1, amount=Asset.hive("1.1"), memo="memo1")

    # TODO: save balances before transfer
    ...

    # ACT
    ### Create 2 transfers
    # Choose transfer operation
    await pilot.press("f2", "tab")

    asset_token: ASSET_TOKEN = "HBD"

    for i in range(2):
        memo = "memo" + str(i)
        amount = "1." + str(i)

        # Fill transfer data
        await pilot.press("enter")
        await fill_transfer_data(pilot, USER1, amount, asset_token, memo)
        log_current_view(pilot.app, nodes=True)

        await pilot.press("f2")  # add to cart (goes back to Operations screen)
        log_current_view(pilot.app)

        asset_token = "HIVE"

    await pilot.press("f2")  # go to cart
    await finalize_transaction(pilot, activated, PASS)

    node.wait_number_of_blocks(1)

    # ASSERT
    history = node.api.account_history.get_account_history(account=USER, include_reversible=True)["history"]
    operation = history[-2][1]["op"]
    tt.logger.debug(f"operation1: {operation}")
    assert (
        operation["type"] == "transfer_operation"
    ), f"Expected 'transfer_operation' type! Current is '{operation['type']}'"
    assert operation["value"] == expected0.dict(by_alias=True), "Transfer operation different than expected!"

    operation = history[-1][1]["op"]
    tt.logger.debug(f"operation2: {operation}")
    assert (
        operation["type"] == "transfer_operation"
    ), f"Expected 'transfer_operation' type! Current is '{operation['type']}'"
    assert operation["value"] == expected1.dict(by_alias=True), "Transfer operation different than expected!"
