from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.data_providers.governance_data_provider import GovernanceDataProvider
from clive.__private.ui.data_providers.proposals_data_provider import ProposalsDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.governance_operations.proposals import Proposals
from clive.__private.ui.operations.governance_operations.proxy import Proxy
from clive.__private.ui.operations.governance_operations.witness import Witnesses
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent

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
        with GovernanceDataProvider(), ProposalsDataProvider(), CliveTabbedContent():
            yield Proxy("Proxy")
            yield Witnesses(WITNESSES_TAB_LABEL)
            yield Proposals(PROPOSALS_TAB_NAME)

    @on(CliveTabbedContent.TabActivated)
    def change_provider_status(self, event: CliveTabbedContent.TabActivated) -> None:
        witnesses_provider = self.query_one(GovernanceDataProvider)
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
