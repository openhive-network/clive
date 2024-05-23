from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from clive.__private.ui.operations.governance_operations.witness.witness import Witness
from clive_local_tools.data.generates import generate_witness_name
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT2_DATA,
    WORKING_ACCOUNT_DATA,
)
from schemas.operations import AccountWitnessVoteOperation

from .checkers import (
    assert_is_focused,
)

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot, OperationProcessing


WITNESSES_PER_PAGE: Final[int] = 30
USER1: Final[str] = WORKING_ACCOUNT_DATA.account.name
USER2: Final[str] = ALT_WORKING_ACCOUNT1_DATA.account.name
USER3: Final[str] = ALT_WORKING_ACCOUNT2_DATA.account.name
OPERATION_PROCESSING_TESTDATA: Final[list[OperationProcessing]] = [
    "FAST_BROADCAST",
    "FINALIZE_TRANSACTION",
    "ADD_TO_CART",
]


async def vote_for_witness(
    pilot: ClivePilot, user: str, expected_witness: str | int | None = None
) -> AccountWitnessVoteOperation:
    assert_is_focused(pilot, Witness)
    witness = cast(Witness, pilot.app.focused)
    if isinstance(expected_witness, int):
        expected_witness = generate_witness_name(expected_witness)
    if expected_witness is not None:
        assert (
            expected_witness == witness.action_identifier
        ), f"Expected witness name: '{expected_witness}', but current is: '{witness.action_identifier}'."
    assert witness.governance_checkbox.value is False, "Expected unmarked checkbox in witness row!"
    await pilot.press("enter")
    assert witness.governance_checkbox.value is True, "Expected marked checkbox in witness row!"

    return AccountWitnessVoteOperation(
        account=user,
        witness=witness.action_identifier,
    )


def find_witness_by_name(pilot: ClivePilot, name: str) -> Witness | None:
    for witness in pilot.app.screen.query(Witness):
        if witness.action_identifier == name:
            return witness
    return None
