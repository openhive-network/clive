from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.operations import OperationButton, Operations
from clive_local_tools.data.generates import generate_witness_name
from clive_local_tools.tui.checkers import (
    assert_active_tab,
    assert_is_focused,
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import press_and_wait_for_screen
from clive_local_tools.tui.witness_votes_utils import (
    USER1,
    find_witness_by_name,
    vote_for_witness,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.tui.types import ClivePilot
    from schemas.operations import AccountWitnessVoteOperation


async def test_user_with_no_votes_has_operations_in_the_cart_and_finalizes_transaction(
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """https://gitlab.syncad.com/hive/clive/-/issues/127#5-test-cases-cart-and-other-way-of-broadcast case 5.2."""
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    expected_operations: list[AccountWitnessVoteOperation] = []

    # ACT
    for i in range(2):
        witness_name = generate_witness_name(4 + i)
        witness = find_witness_by_name(pilot, witness_name)
        pilot.app.screen.set_focus(witness)
        expected_operations.append(await vote_for_witness(pilot, USER1, witness_name))

    await press_and_wait_for_screen(pilot, "f2", Operations)  # add 2 operations to cart
    # Back to Witnesses view
    assert_is_focused(pilot, OperationButton)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")

    witness_name = generate_witness_name(2)
    witness = find_witness_by_name(pilot, witness_name)
    pilot.app.screen.set_focus(witness)
    expected_operations.append(await vote_for_witness(pilot, USER1, witness_name))

    await process_operation(pilot, "FINALIZE_TRANSACTION")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)
