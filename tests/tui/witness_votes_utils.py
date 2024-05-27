from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

import test_tools as tt
from textual.widgets import Label

from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.governance_operations.witness.witness import Witness
from clive.__private.ui.operations.operations import Operations
from clive_local_tools.testnet_block_log.constants import ALT_WORKING_ACCOUNT1, ALT_WORKING_ACCOUNT2, WORKING_ACCOUNT
from clive_local_tools.tui.checkers import (
    assert_active_tab,
    assert_is_focused,
    assert_is_screen_active,
)
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
)
from schemas.operations import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from clive_local_tools.tui.types import ClivePilot


WITNESSES_PER_PAGE: Final[int] = 30
USER1: Final[tt.Account] = WORKING_ACCOUNT
USER2: Final[tt.Account] = ALT_WORKING_ACCOUNT1
USER3: Final[tt.Account] = ALT_WORKING_ACCOUNT2


async def goto_governance_witness_list(pilot: ClivePilot) -> None:
    assert_is_screen_active(pilot, DashboardActive)
    await press_and_wait_for_screen(pilot, "f2", Operations)
    assert_active_tab(pilot, "Financial")
    await pilot.press("right")
    assert_active_tab(pilot, "Social")
    await pilot.press("right")
    assert_active_tab(pilot, "Governance")
    await focus_next(pilot)
    await press_and_wait_for_screen(pilot, "enter", Governance)
    assert_active_tab(pilot, "Proxy")
    await pilot.press("right")
    assert_active_tab(pilot, "Witnesses")


async def vote_witness(
    pilot: ClivePilot, user: str, expected_witness: str | None = None
) -> AccountWitnessVoteOperation:
    return await _create_witness_vote_operation(pilot, user, True, expected_witness)


async def unvote_witness(
    pilot: ClivePilot, user: str, expected_witness: str | None = None
) -> AccountWitnessVoteOperation:
    return await _create_witness_vote_operation(pilot, user, False, expected_witness)


async def _create_witness_vote_operation(
    pilot: ClivePilot, user: str, approve: bool, expected_witness: str | None = None
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


async def goto_first_witness(pilot: ClivePilot, vote_label: Literal["Vote", "Unvote"]) -> None:
    witness: Witness = pilot.app.focused  # type: ignore[assignment]
    label = witness.governance_checkbox.query_one(Label)
    text = str(label.renderable)
    while text != vote_label:
        await focus_next(pilot)
        witness = pilot.app.focused  # type: ignore[assignment]
        label = witness.governance_checkbox.query_one(Label)
        text = str(label.renderable)
