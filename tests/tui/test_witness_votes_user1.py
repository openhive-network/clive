from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.governance_operations.witness.witness import Witness, WitnessActionRow
from clive.__private.ui.operations.governance_operations.witness.witness_details_screen import (
    WitnessDetailsScreen,
    WitnessDetailsWidget,
)
from clive.__private.ui.operations.operations import OperationButton, Operations
from clive_local_tools.tui.checkers import (
    assert_active_tab,
    assert_is_focused,
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
)

from .witness_votes_utils import USER1, WITNESSES_PER_PAGE, goto_governance_witness_list, vote_for_witness

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing
    from schemas.operations import AccountWitnessVoteOperation


USER: Final[str] = USER1

TESTDATA: Final[list[OperationProcessing]] = [
    "FAST_BROADCAST",
    "FINALIZE_TRANSACTION",
    "ADD_TO_CART",
]


@pytest.mark.parametrize("operation_processing", TESTDATA)
async def test_witness_votes_user1_1(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """
    1. Test cases: Vote for one witness.

        1.1. User 1 votes for one witness and then broadcast it (a/b/c).
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_dashboard_active

    # ACT
    await goto_governance_witness_list(pilot)
    await focus_next(pilot)  # go to first witness on list
    expected_operation = await vote_for_witness(pilot, USER)
    await process_operation(pilot, operation_processing, True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


@pytest.mark.parametrize("operation_processing", TESTDATA)
async def test_witness_votes_user1_2(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """
    3. Test cases: Add and remove votes for witnesses.

        3.1. User 1 votes for the first 30 witnesses and then broadcast the transaction (a/b/c).
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_dashboard_active
    expected_operations: list[AccountWitnessVoteOperation] = []
    VOTED_WITNESSES_COUNT: Final[int] = 30  # noqa: N806
    assert VOTED_WITNESSES_COUNT <= WITNESSES_PER_PAGE

    # ACT
    await goto_governance_witness_list(pilot)
    for _ in range(VOTED_WITNESSES_COUNT):
        await focus_next(pilot)  # go to next witness on list
        expected_operations.append(await vote_for_witness(pilot, USER))

    await process_operation(pilot, operation_processing, True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)


async def test_witness_votes_user1_3(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    4. Test cases: Pending operations (cart).

        4.1. User votes for the witnesses one by one.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_dashboard_active
    expected_operations: list[AccountWitnessVoteOperation] = []

    # ACT
    await goto_governance_witness_list(pilot)
    await focus_next(pilot)  # go to first witness on list
    expected_operations.append(await vote_for_witness(pilot, USER))

    await press_and_wait_for_screen(pilot, "f2", Operations)  # add 1 operation to cart
    await press_and_wait_for_screen(pilot, "f2", Cart)

    # ACT
    await press_and_wait_for_screen(pilot, "escape", Operations)  # back to Operations
    assert_is_focused(pilot, OperationButton)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")
    await focus_next(pilot)  # go to first witness on list
    assert_is_focused(pilot, Witness)

    # ASSERT
    actions = pilot.app.screen.query(WitnessActionRow)
    assert len(actions) == 1, f"Expected single pending action! Current number is: {len(actions)} action(s)."

    # ACT
    for _ in range(2):
        await focus_next(pilot)  # go to next witness on list
        expected_operations.append(await vote_for_witness(pilot, USER))

    # ACT
    await process_operation(pilot, "ADD_TO_CART", True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)


async def test_witness_votes_user1_4(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    5. Test cases: Cart and other way of broadcast.

        5.2. Cart and finalize transaction - User 1 has operations in the cart and then finalize transaction.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_dashboard_active
    expected_operations: list[AccountWitnessVoteOperation] = []

    # ACT
    await goto_governance_witness_list(pilot)
    # Assumes order of witnesses: 02 03 01 04 05, so skip some witnesses
    for _ in range(3):
        await focus_next(pilot)  # go to next witness on list
        assert_is_focused(pilot, Witness)

    for i in range(2):
        await focus_next(pilot)  # go to next witness on list
        expected_operations.append(await vote_for_witness(pilot, USER, f"witness-0{4+i}"))

    await press_and_wait_for_screen(pilot, "f2", Operations)  # add 2 operations to cart
    # Back to Witnesses view
    assert_is_focused(pilot, OperationButton)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")

    await focus_next(pilot)  # go to first witness on list
    expected_operations.append(await vote_for_witness(pilot, USER, "witness-02"))

    # ACT
    await process_operation(pilot, "FINALIZE_TRANSACTION", True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)


async def test_witness_votes_user1_5(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    7. Test cases: Check the pages of the witnesses list - vote for the last witness.

        7.1. User 1 votes for the last witness.
    """
    # ARRANGE
    node, _, pilot = prepared_tui_on_dashboard_active

    # ACT
    await goto_governance_witness_list(pilot)
    await focus_next(pilot)  # go to first witness on list
    await pilot.press("pagedown")  # go to next page
    # go to the last Witness
    for _ in range(len(pilot.app.query(Witness)) - 1):
        await focus_next(pilot)  # go to next witness on list
        assert_is_focused(pilot, Witness)

    witness: Witness = pilot.app.focused  # type: ignore[assignment]
    tt.logger.debug(f"witness name: {witness.action_identifier}")
    assert (
        witness.action_identifier == "witness-40"
    ), f"Expected witness name: 'witness-40', but current is: '{witness.action_identifier}'"

    expected_operation = await vote_for_witness(pilot, USER)
    await process_operation(pilot, "FAST_BROADCAST", True)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


async def test_witness_votes_user1_6(
    prepared_tui_on_dashboard_active: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """
    9. Test cases: Check if the witness details are displayed.

        9.1. Check if all information about witness are displayed:
        a. Time of the query
        b. url
        c. created
        d. missed blocks
        e. price feed
        f. version
    """
    # ARRANGE
    _, _, pilot = prepared_tui_on_dashboard_active

    # ACT
    await goto_governance_witness_list(pilot)
    await focus_next(pilot)  # go to first witness on list
    witness: Witness = pilot.app.focused  # type: ignore[assignment]
    tt.logger.debug(f"witness name: {witness.action_identifier}")

    await press_and_wait_for_screen(pilot, "f3", WitnessDetailsScreen, wait_for_focused=False)
    witness_details_str = ""
    POOL_TIME: Final[int] = 2  # noqa: N806 # details are refreshed every 1.5 sec
    for _ in range(int(TUI_TESTS_GENERAL_TIMEOUT) // POOL_TIME):
        await pilot.pause(POOL_TIME)
        witness_details = pilot.app.screen.query_one(WitnessDetailsWidget)
        witness_details_str = str(witness_details.renderable)
        if witness_details_str is not None and witness_details_str != "":
            break

    for text in ("Time of the query", "url", "created", "missed blocks", "price feed", "version"):
        # ASSERT
        assert (
            witness_details_str.find(text) != -1
        ), f"Information detail '{text}' not found in '{witness_details_str}'!"

    await press_and_wait_for_screen(pilot, "escape", Governance)
