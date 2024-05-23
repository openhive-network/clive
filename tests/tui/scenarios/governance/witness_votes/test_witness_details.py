from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.ui.operations.governance_operations.governance_operations import Governance
from clive.__private.ui.operations.governance_operations.witness.witness_details_screen import (
    WitnessDetailsScreen,
    WitnessDetailsWidget,
)
from clive_local_tools.tui.constants import TUI_TESTS_GENERAL_TIMEOUT
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.tui.types import ClivePilot


async def test_if_all_information_about_witness_details_is_displayed(
    prepared_tui_on_witnesses_screen: tuple[tt.RawNode, tt.Wallet, ClivePilot],
) -> None:
    """https://gitlab.syncad.com/hive/clive/-/issues/127#9-test-cases-check-if-the-witness-details-are-displayed case 9.1."""  # noqa: E501
    # ARRANGE
    _, _, pilot = prepared_tui_on_witnesses_screen

    # ACT
    await focus_next(pilot)  # go to first witness on list

    await press_and_wait_for_screen(pilot, "f3", WitnessDetailsScreen, wait_for_focused=False)
    witness_details_str = ""
    POOL_TIME: Final[int] = 2  # noqa: N806 # details are refreshed every 1.5 sec
    for _ in range(int(TUI_TESTS_GENERAL_TIMEOUT) // POOL_TIME):
        await pilot.pause(POOL_TIME)
        witness_details = pilot.app.screen.query_one(WitnessDetailsWidget)
        witness_details_str = str(witness_details.renderable)
        if witness_details_str is not None and witness_details_str != "":
            break

    # ASSERT
    for text in ("Time of the query", "url", "created", "missed blocks", "price feed", "version"):
        assert (
            witness_details_str.find(text) != -1
        ), f"Information detail '{text}' not found in '{witness_details_str}'!"

    await press_and_wait_for_screen(pilot, "escape", Governance)
