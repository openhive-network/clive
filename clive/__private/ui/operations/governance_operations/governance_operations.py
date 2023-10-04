from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.css.query import NoMatches
from textual.widgets import Label, Static, TabbedContent

from clive.__private.ui.operations.governance_operations.governance_data import GovernanceData, GovernanceDataProvider
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.witness_checkbox import WitnessCheckbox

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.models.aliased import WitnessType


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


class WitnessesList(ScrollableContainer):
    def __init__(self, witnesses: list[WitnessType] | None):
        super().__init__()
        self.__witnesses = witnesses

    def compose(self) -> ComposeResult:
        if self.__witnesses is not None:
            yield Static("Modify the votes for witnesses", id="witnesses-headline")
            yield WitnessesListHeader()
            for rank, witness in enumerate(self.__witnesses, start=1):
                yield Witness(rank, witness.owner, str(witness.votes))
                yield Static()


class WitnessesListHeader(Grid):
    def compose(self) -> ComposeResult:
        yield Static()
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")
        yield Static()


class Proxy(ScrollableTabPane):
    """TabPane with all content about proxy."""


class Proposals(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Witnesses(ScrollableTabPane):
    """TabPane with all content about witnesses."""

    def __init__(self, provider: GovernanceDataProvider, title: TextType) -> None:
        super().__init__(title=title)
        self.__provider = provider

    def compose(self) -> ComposeResult:
        yield WitnessesList(self.__provider.content.top_100_witnesses)

    def on_mount(self) -> None:
        self.watch(self.__provider, "content", callback=self.__sync_witnesses_list)

    def __sync_witnesses_list(self, content: GovernanceData) -> None:
        try:
            witnesses_list_container = self.query_one(WitnessesList)
        except NoMatches:
            return

        witnesses_list_container.remove()
        new_transfers_item = WitnessesList(content.top_100_witnesses)
        self.mount(new_transfers_item)


class Governance(OperationBaseScreen):
    def create_left_panel(self) -> ComposeResult:
        with GovernanceDataProvider() as provider, TabbedContent():
            yield Proxy("Proxy")
            yield Witnesses(provider, "Witnesses")
            yield Proposals("Proposals")
