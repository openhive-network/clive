from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Grid
from textual.css.query import NoMatches
from textual.widgets import Label, Static, TabbedContent

from clive.__private.ui.operations.governance_operations.governance_data import GovernanceData, GovernanceDataProvider
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.witness_checkbox import WitnessCheckbox

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.models.aliased import WitnessType


class Witness(Grid):
    def __init__(self, rank: int, name: str, votes: int, is_voted: bool = False) -> None:
        super().__init__()
        self.__rank = rank
        self.__name = name
        self.__votes = votes
        self.__is_voted = is_voted

    def compose(self) -> ComposeResult:
        yield WitnessCheckbox(is_voted=self.__is_voted)
        yield Label(str(self.__rank), classes="witness-rank")
        yield Label(self.__name, classes="witness-name")
        yield Label(str(self.__votes), classes="witness-votes")
        yield Label("details", classes="witness-details")


class WitnessesList(Container):
    def __init__(self, witnesses: list[WitnessType] | None, first_witness_index: int):
        super().__init__()
        self.__witnesses = witnesses
        self.__first_witness_index = first_witness_index

    def compose(self) -> ComposeResult:
        for rank, witness in enumerate(
            self.__witnesses[self.__first_witness_index : self.__first_witness_index + 15],  # type: ignore[index]
            start=self.__first_witness_index + 1,
        ):
            yield Witness(rank, witness.owner, witness.votes)
            yield Static()


class WitnessesListHeader(Grid):
    def compose(self) -> ComposeResult:
        yield Static()
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")
        yield Static()


class WitnessesTable(Container, CliveWidget):
    can_focus = True

    def __init__(self, witnesses: list[WitnessType] | None):
        super().__init__()
        self.__witnesses = witnesses
        self.__witness_index = 0

    def compose(self) -> ComposeResult:
        yield Static("Modify the votes for witnesses", id="witnesses-headline")
        yield WitnessesListHeader()
        yield WitnessesList(self.__witnesses, self.__witness_index)

    def on_focus(self) -> None:
        self.bind(Binding("left", "previous_page", "previous page"))
        self.bind(Binding("right", "next_page", "next page"))

    def action_next_page(self) -> None:
        last_possible_index = 90
        if self.__witness_index == last_possible_index:
            self.notify("Just 105 witnesses are available, please type witness outside the list and vote beside")
            return

        self.query_one(WitnessesList).remove()
        self.__witness_index += 15
        next_witnesses_page = WitnessesList(self.__witnesses, self.__witness_index)
        self.mount(next_witnesses_page)
        return

    def action_previous_page(self) -> None:
        if self.__witness_index == 0:
            self.notify("Cannot switch to previous page")
            return

        self.query_one(WitnessesList).remove()
        self.__witness_index -= 15
        next_witnesses_page = WitnessesList(self.__witnesses, self.__witness_index)
        self.mount(next_witnesses_page)
        return


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
        yield WitnessesTable(self.__provider.content.top_100_witnesses)

    def on_mount(self) -> None:
        self.watch(self.__provider, "content", callback=self.__sync_witnesses_list)

    def __sync_witnesses_list(self, content: GovernanceData) -> None:
        try:
            witnesses_list_container = self.query_one(WitnessesTable)
        except NoMatches:
            return

        witnesses_list_container.remove()
        new_witnesses_table_container = WitnessesTable(content.top_100_witnesses)
        self.mount(new_witnesses_table_container)


class Governance(OperationBaseScreen):
    def create_left_panel(self) -> ComposeResult:
        with GovernanceDataProvider() as provider, TabbedContent():
            yield Proxy("Proxy")
            yield Witnesses(provider, "Witnesses")
            yield Proposals("Proposals")
