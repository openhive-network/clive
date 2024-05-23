from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.ui.operations.governance_operations.witness.witness import Witness
from clive_local_tools.data.generates import generate_witness_name
from clive_local_tools.testnet_block_log.constants import WITNESS_LAST_INDEX
from clive_local_tools.tui.checkers import (
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_focus,
    wait_for_focus,
)
from clive_local_tools.tui.witness_votes_utils import (
    USER1,
    vote_for_witness,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.tui.types import ClivePilot


async def test_voting_for_last_witness(
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """https://gitlab.syncad.com/hive/clive/-/issues/127#7-test-cases-check-the-pages-of-the-witnesses-list---vote-for-the-last-witness case 7.1."""  # noqa: E501
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen

    # ACT
    witnesses_tab_name = pilot.app.focused
    await focus_next(pilot)  # go to first witness on list
    await press_and_wait_for_focus(pilot, "pagedown")  # go to next page
    # to be sure focus is on witness list, not "witnesses" tab name:
    await wait_for_focus(pilot, different_than=witnesses_tab_name)
    # go to the last Witness
    witness = pilot.app.screen.query(Witness).last()
    pilot.app.screen.set_focus(witness)
    last_witness_name = generate_witness_name(WITNESS_LAST_INDEX)
    assert (
        witness.action_identifier == last_witness_name
    ), f"Expected witness name: '{last_witness_name}', but current is: '{witness.action_identifier}'"

    expected_operation = await vote_for_witness(pilot, USER1)
    await process_operation(pilot, "FAST_BROADCAST")

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)
