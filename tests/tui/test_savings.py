from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import pytest
import test_tools as tt

from clive.__private.ui.operations.savings_operations.savings_operations import PendingTransfer, Savings
from clive_local_tools.tui.activate import activate
from clive_local_tools.tui.choose_asset_token import choose_asset_token
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT
from clive_local_tools.tui.fast_broadcast import fast_broadcast
from clive_local_tools.tui.finalize_transaction import finalize_transaction
from clive_local_tools.tui.textual import write_text
from clive_local_tools.tui.utils import current_view, get_mode

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from textual.pilot import Pilot

    from clive.__private.ui.app import Clive
    from clive_local_tools.tui.types import ASSET_TOKEN, OPERATION_PROCESSING


USER: Final[str] = WORKING_ACCOUNT.name
PASS: Final[str] = WORKING_ACCOUNT.name
USER1: Final[str] = WATCHED_ACCOUNTS[0].name
AMOUNT: Final[str] = "1.07"


async def create_savings(  # noqa: PLR0913
    pilot: Pilot[int],
    to: bool,  # True for transfer to savings, False for transfer from savings
    other_account: str | None,  # None means using current profile account name
    amount: str,
    asset_token: ASSET_TOKEN,
    memo: str | None,
) -> None:
    """Assuming Savings is current screen."""
    assert isinstance(
        pilot.app.screen, Savings
    ), f"'create_savings' requires 'Savings' to be the current screen! Current screen is: '{pilot.app.screen}'."
    await pilot.press("tab")
    if not to:
        await pilot.press("right", "space")
    await pilot.press("tab")
    if other_account:
        await pilot.press("ctrl+w")
        await write_text(pilot, other_account)
    await pilot.press("tab")
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


@pytest.mark.parametrize(("memo", "operation_processing"), testdata)
@pytest.mark.parametrize("asset_token", ["HIVE", "HBD"])
@pytest.mark.parametrize("other_account", [None, USER1])
@pytest.mark.parametrize("to", ["True", "False"])
@pytest.mark.parametrize("activated", ["True", "False"])
async def test_savings(  # noqa: PLR0913
    prepared_env: tuple[tt.InitNode, Clive],
    request: FixtureRequest,
    activated: bool,
    to: bool,  # True for transfer to savings, False for transfer from savings
    other_account: str | None,  # None means using current profile account name
    asset_token: ASSET_TOKEN,
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
    tt.logger.debug(f"Enter '{request.node.name}' ...")
    node, app = prepared_env

    # ARRANGE
    async with app.run_test() as pilot:
        current_view(app, True)
        assert get_mode(app) == "inactive", "Expected 'inactive' mode!"

        if activated:
            await activate(pilot, PASS)
            assert get_mode(app) == "active", "Expected 'active' mode!"

        # TODO: save balances before transfer
        ...

        ### Create transfer to savings
        # Go to savings operation
        await pilot.press("f2", "tab", "tab", "enter", "right")

        # Fill transfer data
        await create_savings(pilot, to, other_account, AMOUNT, asset_token, memo)
        current_view(app, True)

        # ACT
        if operation_processing == "FAST_BROADCAST":
            await fast_broadcast(pilot, activated, PASS)
        else:  # "ADD_TO_CART" or "FINALIZE_TRANSACTION"
            if operation_processing == "ADD_TO_CART":
                await pilot.press("f2", "f2")  # add to cart, go to cart
            await finalize_transaction(pilot, activated, PASS)

        node.wait_number_of_blocks(1)

        # ASSERT
        history = node.api.account_history.get_account_history(account=USER, include_reversible=True)["history"]
        operation = history[-1][1]["op"]
        tt.logger.debug(f"operation: {operation}")

        if to:
            assert (
                operation["type"] == "transfer_to_savings_operation"
            ), f"Expected 'transfer_to_savings_operation' type! Current is '{operation['type']}'"
        else:
            assert (
                operation["type"] == "transfer_from_savings_operation"
            ), f"Expected 'transfer_from_savings_operation' type! Current is '{operation['type']}'"

        expected: dict[str, Any] = {
            "from": USER,
            "to": other_account if other_account else USER,
            "amount": {
                "amount": str(int(float(AMOUNT) * 1000)),
                "precision": 3,
                "nai": "@@000000021" if asset_token == "HIVE" else "@@000000013",
            },
            "memo": memo if memo else "",
        }
        if not to:
            expected["request_id"] = 0
        assert operation["value"] == expected, "Transfer operation different than expected!"

        if to is False:
            await pilot.press("esc", "f2", "tab", "tab", "enter")  # go to savings
            pending_transfer = app.query(PendingTransfer)
            assert (
                len(pending_transfer.nodes) == 1
            ), f"Expected 1 transfer! Transfers' count: {len(pending_transfer.nodes)}"

        if to is False:  # test canceling transfer from savings
            # ARRANGE & ACT
            await pilot.press("tab", "enter")  # Cancel transfer

            # ASSERT
            await pilot.press("enter")  # go to savings
            pending_transfer = app.query(PendingTransfer)
            assert len(pending_transfer.nodes) == 0, "Expected no pending transfers!"

        ### Quit
        await clive_quit(pilot)


@pytest.mark.parametrize("other_account", [None, USER1])
@pytest.mark.parametrize("to", ["True", "False"])
@pytest.mark.parametrize("activated", ["True", "False"])
async def test_cancel_transfers_from_savings(
    prepared_env: tuple[tt.InitNode, Clive],
    request: FixtureRequest,
    activated: bool,
    to: bool,  # True for transfer to savings, False for transfer from savings
    other_account: str | None,  # None means using current profile account name
) -> None:
    """
    #110: I-IV (create transfer to/from savings) and V-VI (cancel transfer from savings).

    Clive is activated/deactivated. Then:
    4. The user makes two operations to own account/another account, the first in HBD, the second in HIVE,
       adds them to cart and then broadcasts.
    """
    tt.logger.debug(f"Enter '{request.node.name}' ...")
    node, app = prepared_env

    # ARRANGE
    async with app.run_test() as pilot:
        current_view(app, True)
        assert get_mode(app) == "inactive", "Expected 'inactive' mode!"

        if activated:
            await activate(pilot, PASS)
            assert get_mode(app) == "active", "Expected 'active' mode!"

        # TODO: save balances before transfer
        ...

        # ACT
        ### Create 2 transfers
        # Choose savings operation
        await pilot.press("f2", "tab", "tab")

        asset_token: ASSET_TOKEN = "HBD"

        for i in range(2):
            memo = "memo" + str(i)
            amount = "2." + str(i)

            # Fill transfer data
            await pilot.press("enter", "right")  # go to savings operation
            await create_savings(pilot, to, other_account, amount, asset_token, memo)
            current_view(app, True)

            await pilot.press("f2")  # add to cart (goes back to Operations screen)
            current_view(app)

            asset_token = "HIVE"

        await pilot.press("f2")  # go to cart
        await finalize_transaction(pilot, activated, PASS)

        node.wait_number_of_blocks(1)

        # ASSERT
        history = node.api.account_history.get_account_history(account=USER, include_reversible=True)["history"]
        operation = history[-2][1]["op"]
        tt.logger.debug(f"operation1: {operation}")
        if to:
            assert (
                operation["type"] == "transfer_to_savings_operation"
            ), f"Expected 'transfer_to_savings_operation' type! Current is '{operation['type']}'"
        else:
            assert (
                operation["type"] == "transfer_from_savings_operation"
            ), f"Expected 'transfer_from_savings_operation' type! Current is '{operation['type']}'"
        expected: dict[str, Any] = {
            "from": USER,
            "to": other_account if other_account else USER,
            "amount": {"amount": "2000", "precision": 3, "nai": "@@000000013"},
            "memo": "memo0",
        }
        if not to:
            expected["request_id"] = 0
        assert operation["value"] == expected, "Transfer operation different than expected!"

        operation = history[-1][1]["op"]
        tt.logger.debug(f"operation2: {operation}")
        if to:
            assert (
                operation["type"] == "transfer_to_savings_operation"
            ), f"Expected 'transfer_to_savings_operation' type! Current is '{operation['type']}'"
        else:
            assert (
                operation["type"] == "transfer_from_savings_operation"
            ), f"Expected 'transfer_from_savings_operation' type! Current is '{operation['type']}'"
        expected = {
            "from": USER,
            "to": other_account if other_account else USER,
            "amount": {"amount": "2100", "precision": 3, "nai": "@@000000021"},
            "memo": "memo1",
        }
        if not to:
            expected["request_id"] = 1
        assert operation["value"] == expected, "Transfer operation different than expected!"

        if to is False:
            await pilot.press("f2", "tab", "tab", "enter")  # go to savings
            current_view(app, True)
            pending_transfer = app.query(PendingTransfer)
            assert (
                len(pending_transfer.nodes) == 2  # noqa: PLR2004
            ), f"Expected 2 transfers! Transfers' count: {len(pending_transfer.nodes)}"

        if to is False:
            # Test canceling first transfer from savings
            # ARRANGE & ACT
            await pilot.press("tab", "enter")  # Cancel transfer
            await fast_broadcast(pilot, activated)

            # ASSERT
            await pilot.press("enter")  # go to savings
            current_view(app, True)
            pending_transfer = app.query(PendingTransfer)
            assert (
                len(pending_transfer.nodes) == 1
            ), f"Expected 1 transfer! Transfers' count: {len(pending_transfer.nodes)}"

            # Test canceling second transfer from savings
            # ARRANGE & ACT
            await pilot.press("tab", "enter")  # Cancel transfer
            await finalize_transaction(pilot, activated)

            # ASSERT
            await pilot.press("f2", "tab", "tab", "enter")  # go to savings
            current_view(app, True)
            pending_transfer = app.query(PendingTransfer)
            assert len(pending_transfer.nodes) == 0, "Expected no pending transfers!"

        ### Quit
        await clive_quit(pilot)
