from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.data_providers.proposals_data_provider import ProposalsDataProvider
from clive.__private.ui.data_providers.witnesses_data_provider import WitnessesDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.governance_operations.proposals.proposals import Proposals
from clive.__private.ui.operations.governance_operations.proxy.proxy import Proxy
from clive.__private.ui.operations.governance_operations.witness.witness import Witnesses
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult

WITNESSES_TAB_LABEL: Final[str] = "Witnesses"
PROPOSALS_TAB_NAME: Final[str] = "Proposals"


class Governance(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with WitnessesDataProvider(paused=True), ProposalsDataProvider(paused=True), CliveTabbedContent():
            yield Proxy("Proxy")
            yield Witnesses(WITNESSES_TAB_LABEL)
            yield Proposals(PROPOSALS_TAB_NAME)

    @on(CliveTabbedContent.TabActivated)
    def _tab_changed(self, event: CliveTabbedContent.TabActivated) -> None:
        # change provider status based on the tab
        witnesses_provider = self.query_one(WitnessesDataProvider)
        proposals_provider = self.query_one(ProposalsDataProvider)

        if str(event.tab.label) == PROPOSALS_TAB_NAME:
            witnesses_provider.pause()
            proposals_provider.restart()
        elif str(event.tab.label) == WITNESSES_TAB_LABEL:
            proposals_provider.pause()
            witnesses_provider.restart()
        else:
            witnesses_provider.pause()
            proposals_provider.pause()

        # clear all the input values and validation results
        inputs = self.query(CliveValidatedInput)  # type: ignore[type-abstract]
        for input_obj in inputs:
            input_obj.clear_validation()
