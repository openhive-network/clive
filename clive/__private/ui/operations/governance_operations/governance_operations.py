from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Label, Static, TabbedContent

from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.witness_checkbox import WitnessCheckbox

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Witness(Grid):
    def __init__(self, rank: int, name: str, votes: str) -> None:
        super().__init__()
        self.__rank = rank
        self.__name = name
        self.__votes = votes

    def compose(self) -> ComposeResult:
        yield WitnessCheckbox()
        yield Label(str(self.__rank), classes="witness-rank")
        yield Label(self.__name, classes="witness-name")
        yield Label(self.__votes, classes="witness-votes")
        yield Label("details", classes="witness-details")


class Proxy(ScrollableTabPane):
    """TabPane with all content about proxy."""


class Proposals(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Witnesses(ScrollableTabPane):
    """TabPane with all content about witnesses."""

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="witnesses"):
            yield Witness(1, "blockades", "78M HP")
            yield Static()


class Governance(OperationBaseScreen):
    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield Proxy("Proxy")
            yield Witnesses("Witnesses")
            yield Proposals("Proposals")
