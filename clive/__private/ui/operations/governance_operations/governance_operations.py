from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import TabbedContent

from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Proxy(ScrollableTabPane):
    """TabPane with all content about proxy."""


class Proposals(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Witnesses(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Governance(OperationBaseScreen):
    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield Proxy("Proxy")
            yield Witnesses("Witnesses")
            yield Proposals("Proposals")
