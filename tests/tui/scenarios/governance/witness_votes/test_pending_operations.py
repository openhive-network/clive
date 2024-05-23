from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.governance_operations.witness.witness import Witness, WitnessActionRow
from clive.__private.ui.operations.operations import OperationButton, Operations
from clive_local_tools.tui.checkers import (
    assert_active_tab,
    assert_is_focused,
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
)
from clive_local_tools.tui.witness_votes_utils import (
    USER1,
    vote_for_witness,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.tui.types import ClivePilot
    from schemas.operations import AccountWitnessVoteOperation


async def test_user_with_no_votes_adds_votes_one_by_one(
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """https://gitlab.syncad.com/hive/clive/-/issues/127#4-test-cases-pending-operations-cart case 4.1."""
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    expected_operations: list[AccountWitnessVoteOperation] = []

    # ACT
    await focus_next(pilot)  # go to first witness on list
    expected_operations.append(await vote_for_witness(pilot, USER1))

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
        expected_operations.append(await vote_for_witness(pilot, USER1))

    # ACT
    await process_operation(pilot, "ADD_TO_CART")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)
