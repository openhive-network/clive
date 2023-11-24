from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.governance_operations.governance_data import GovernanceDataProvider
from clive.__private.ui.operations.governance_operations.proxy import Proxy
from clive.__private.ui.operations.governance_operations.witness import Witnesses
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Proposals(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Governance(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with GovernanceDataProvider(), CliveTabbedContent():
            yield Proxy("Proxy")
            yield Witnesses("Witnesses")
            yield Proposals("Proposals")
