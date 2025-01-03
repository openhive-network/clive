from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on

from clive.__private.ui.data_providers.proposals_data_provider import ProposalsDataProvider
from clive.__private.ui.data_providers.witnesses_data_provider import WitnessesDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
from clive.__private.ui.screens.operations.governance_operations.proposals.proposals import Proposals
from clive.__private.ui.screens.operations.governance_operations.proxy.proxy import Proxy
from clive.__private.ui.screens.operations.governance_operations.witness.witness import Witnesses
from clive.__private.ui.widgets.clive_basic import CliveTabbedContent

if TYPE_CHECKING:
    from textual.app import ComposeResult


GovernanceTabType = Literal["proxy", "witnesses", "proposals"]


class Governance(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, initial_tab: GovernanceTabType = "proxy") -> None:
        super().__init__()
        self._initial_tab = initial_tab

    def create_left_panel(self) -> ComposeResult:
        with WitnessesDataProvider(paused=True), ProposalsDataProvider(paused=True), CliveTabbedContent(
            initial=self._initial_tab
        ):
            yield Proxy("Proxy")
            yield Witnesses("Witnesses")
            yield Proposals("Proposals")

    @on(CliveTabbedContent.TabActivated)
    def change_provider_status(self, event: CliveTabbedContent.TabActivated) -> None:
        witnesses_provider = self.query_exactly_one(WitnessesDataProvider)
        proposals_provider = self.query_exactly_one(ProposalsDataProvider)

        active_pane = event.tabbed_content.active_pane
        if isinstance(active_pane, Proposals):
            witnesses_provider.pause()
            proposals_provider.restart()
        elif isinstance(active_pane, Witnesses):
            proposals_provider.pause()
            witnesses_provider.restart()
        else:
            witnesses_provider.pause()
            proposals_provider.pause()
