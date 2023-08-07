from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import TabbedContent

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ProxyTab(ScrollableTabPane):
    """Tab with all activities related with proxy."""


class WitnessesTab(ScrollableTabPane):
    """Tab with all activities related with witnesses."""


class ProposalsTab(ScrollableTabPane):
    """Tab with all activities related with witnesses."""


class Governance(CartBasedScreen):
    BINDINGS = [Binding("escape", "pop_screen", "Cancel")]

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield ProxyTab("Proxy")
            yield WitnessesTab("Witnesses")
            yield ProposalsTab("Proposals")
