from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

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
USER1: Final[str] = WORKING_ACCOUNT.name
USER2: Final[str] = ALT_WORKING_ACCOUNT1.name
USER3: Final[str] = ALT_WORKING_ACCOUNT2.name


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


async def vote_for_witness(
    pilot: ClivePilot, user: str, expected_witness: str | None = None
) -> AccountWitnessVoteOperation:
    assert_is_focused(pilot, Witness)
    witness: Witness = pilot.app.focused  # type: ignore[assignment]
    tt.logger.debug(f"witness name: {witness.action_identifier}")
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
