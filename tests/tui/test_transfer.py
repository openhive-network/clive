from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.ui.operations.transfer_to_account.transfer_to_account import TransferToAccount
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
AMOUNT: Final[str] = "1.03"


async def create_transfer(
    pilot: Pilot[int], beneficient: str, amount: str, asset_token: ASSET_TOKEN, memo: str | None
) -> None:
    """Assuming Transfer is current screen."""
    assert isinstance(pilot.app.screen, TransferToAccount), (
        "'create_transfer' requires 'TransferToAccount' to be the current screen! Current screen is:"
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
async def test_transfers(  # noqa: PLR0913
    prepared_env: tuple[tt.InitNode, Clive],
    request: FixtureRequest,
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
        ### Create transfer
        # Choose transfer operation
        await pilot.press("f2", "tab", "enter")
        # Fill transfer data
        await create_transfer(pilot, USER1, AMOUNT, asset_token, memo)
        current_view(app, True)

        if operation_processing == "FAST_BROADCAST":
            await fast_broadcast(pilot, activated, PASS)
        else:  # "ADD_TO_CART" or "FINALIZE_TRANSACTION"
            if operation_processing == "ADD_TO_CART":
                await pilot.press("f2", "f2")  # add to cart, go to cart
            await finalize_transaction(pilot, activated, PASS)

        current_view(app)

        node.wait_number_of_blocks(1)

        # ASSERT
        history = node.api.account_history.get_account_history(account=USER, include_reversible=True)["history"]
        operation = history[-1][1]["op"]
        tt.logger.debug(f"operation: {operation}")
        assert (
            operation["type"] == "transfer_operation"
        ), f"Expected 'transfer_operation' type! Current is '{operation['type']}'"
        expected = {
            "from": USER,
            "to": USER1,
            "amount": {
                "amount": str(int(float(AMOUNT) * 1000)),
                "precision": 3,
                "nai": "@@000000021" if asset_token == "HIVE" else "@@000000013",
            },
            "memo": memo if memo else "",
        }
        assert operation["value"] == expected, "Transfer operation different than expected!"

        ### Quit
        await clive_quit(pilot)


@pytest.mark.parametrize("activated", [True, False])
async def test_transfers_finalize_cart(
    prepared_env: tuple[tt.InitNode, Clive], request: FixtureRequest, activated: bool
) -> None:
    """
    #103: I.4, II.4.

    Clive in activated/deactivated modes. Then:
    4. The user makes two transfers, the first in HBD, the second in HIVE, adds them to cart and then broadcasts.
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
        # Choose transfer operation
        await pilot.press("f2", "tab")

        asset_token: ASSET_TOKEN = "HBD"

        for i in range(2):
            memo = "memo" + str(i)
            amount = "1." + str(i)

            # Fill transfer data
            await pilot.press("enter")
            await create_transfer(pilot, USER1, amount, asset_token, memo)
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
        assert (
            operation["type"] == "transfer_operation"
        ), f"Expected 'transfer_operation' type! Current is '{operation['type']}'"
        expected = {
            "from": USER,
            "to": USER1,
            "amount": {"amount": "1000", "precision": 3, "nai": "@@000000013"},
            "memo": "memo0",
        }
        assert operation["value"] == expected, "Transfer operation different than expected!"

        operation = history[-1][1]["op"]
        tt.logger.debug(f"operation2: {operation}")
        assert (
            operation["type"] == "transfer_operation"
        ), f"Expected 'transfer_operation' type! Current is '{operation['type']}'"
        expected = {
            "from": USER,
            "to": USER1,
            "amount": {"amount": "1100", "precision": 3, "nai": "@@000000021"},
            "memo": "memo1",
        }
        assert operation["value"] == expected, "Transfer operation different than expected!"

        ### Quit
        await clive_quit(pilot)
