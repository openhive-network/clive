from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

import test_tools as tt
from textual.widgets import Label

from clive.__private.ui.operations.governance_operations.witness.witness import Witness
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT2_DATA,
    WORKING_ACCOUNT_DATA,
)
from schemas.operations import AccountWitnessVoteOperation

from .checkers import assert_is_focused
from .textual_helpers import focus_next

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing


WITNESSES_PER_PAGE: Final[int] = 30
USER1: Final[tt.Account] = WORKING_ACCOUNT_DATA.account
USER2: Final[tt.Account] = ALT_WORKING_ACCOUNT1_DATA.account
USER3: Final[tt.Account] = ALT_WORKING_ACCOUNT2_DATA.account
OPERATION_PROCESSING_TESTDATA: Final[list[OperationProcessing]] = [
    "FAST_BROADCAST",
    "FINALIZE_TRANSACTION",
    "ADD_TO_CART",
]


async def vote_witness(
    pilot: ClivePilot, user: str, expected_witness: str | None = None
) -> AccountWitnessVoteOperation:
    return await _create_witness_vote_operation(pilot, user, expected_witness, approve=True)


async def unvote_witness(
    pilot: ClivePilot, user: str, expected_witness: str | None = None
) -> AccountWitnessVoteOperation:
    return await _create_witness_vote_operation(pilot, user, expected_witness, approve=False)


async def _create_witness_vote_operation(
    pilot: ClivePilot, user: str, expected_witness: str | None = None, *, approve: bool
) -> AccountWitnessVoteOperation:
    assert_is_focused(pilot, Witness)
    witness: Witness = pilot.app.focused  # type: ignore[assignment]
    tt.logger.debug(f"witness name: {witness.action_identifier}, voted: {witness.governance_checkbox.value}")
    if expected_witness is not None:
        assert (
            expected_witness == witness.action_identifier
        ), f"Expected witness name: '{expected_witness}', but current is: '{witness.action_identifier}'."
    label = witness.governance_checkbox.query_one(Label)
    text = str(label.renderable)
    assert text == ("Vote" if approve else "Unvote"), (
        "Expected 'Vote' in witness row!" if approve else "Expected 'Unvote' in witness row!"
    )
    assert witness.governance_checkbox.value is False, "Expected unmarked checkbox in witness row!"
    await pilot.press("enter")
    assert witness.governance_checkbox.value is True, "Expected marked checkbox in witness row!"

    return AccountWitnessVoteOperation(
        account=user,
        witness=witness.action_identifier,
        approve=approve,
    )


def find_witness_by_name(pilot: ClivePilot, name: str) -> Witness | None:
    for witness in pilot.app.screen.query(Witness):
        if witness.action_identifier == name:
            return witness
    return None


async def goto_first_witness(pilot: ClivePilot, vote_label: Literal["Vote", "Unvote"]) -> None:
    witness: Witness = pilot.app.focused  # type: ignore[assignment]
    label = witness.governance_checkbox.query_one(Label)
    text = str(label.renderable)
    while text != vote_label:
        await focus_next(pilot)
        witness = pilot.app.focused  # type: ignore[assignment]
        label = witness.governance_checkbox.query_one(Label)
        text = str(label.renderable)
