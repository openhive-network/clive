from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.tui.checkers import (
    assert_operations_placed_in_blockchain,
)
from clive_local_tools.tui.notifications import extract_transaction_id_from_notification
from clive_local_tools.tui.process_operation import process_operation
from clive_local_tools.tui.textual_helpers import (
    focus_next,
)
from clive_local_tools.tui.witness_votes_utils import (
    OPERATION_PROCESSING_TESTDATA,
    USER1,
    WITNESSES_PER_PAGE,
    vote_for_witness,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.tui.types import ClivePilot, OperationProcessing
    from schemas.operations import AccountWitnessVoteOperation


@pytest.mark.parametrize("operation_processing", OPERATION_PROCESSING_TESTDATA)
async def test_user_with_no_votes_votes_for_one_witness(
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """https://gitlab.syncad.com/hive/clive/-/issues/127#1-test-cases-vote-for-one-witness case 1.1."""
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen

    # ACT
    await focus_next(pilot)  # go to first witness on list
    expected_operation = await vote_for_witness(pilot, USER1)
    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, expected_operation)


@pytest.mark.parametrize("operation_processing", OPERATION_PROCESSING_TESTDATA)
async def test_user_with_no_votes_votes_for_the_max_number_of_allowed_witness(
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
    operation_processing: OperationProcessing,
) -> None:
    """https://gitlab.syncad.com/hive/clive/-/issues/127#1-test-cases-vote-for-one-witness case 1.4."""
    # ARRANGE
    node, _, pilot = prepared_tui_on_witnesses_screen
    expected_operations: list[AccountWitnessVoteOperation] = []
    VOTED_WITNESSES_COUNT: Final[int] = 30  # noqa: N806
    assert (
        VOTED_WITNESSES_COUNT <= WITNESSES_PER_PAGE
    ), "Expected number of witnesses displayed per page is not less than maximum number of votes for witnesses."

    # ACT
    for _ in range(VOTED_WITNESSES_COUNT):
        await focus_next(pilot)  # go to next witness on list
        expected_operations.append(await vote_for_witness(pilot, USER1))

    await process_operation(pilot, operation_processing)

    transaction_id = await extract_transaction_id_from_notification(pilot)

    # Wait for transaction be available in block
    node.wait_number_of_blocks(1)

    # ASSERT
    assert_operations_placed_in_blockchain(node, transaction_id, *expected_operations)
