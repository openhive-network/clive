from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Label, Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings.multiply_operation_actions_bindings import MultiplyOperationsActionsBindings
from clive.__private.ui.operations.governance_operations.governance_data import GovernanceData, GovernanceDataProvider
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.witness_checkbox import WitnessCheckbox, WitnessCheckBoxChanged
from schemas.operations.account_witness_vote_operation import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.operations.governance_operations.governance_data import Witness as WitnessT
    from clive.models import Operation


class Witness(Grid):
    """The class first checks if there is a witness in the action table - if so, move True to the WitnessCheckbox parameter."""

    def __init__(self, witness: WitnessT) -> None:
        super().__init__()
        self.__witness = witness

        self.__witness_checkbox = WitnessCheckbox(is_voted=witness.voted)

    def compose(self) -> ComposeResult:
        yield self.__witness_checkbox
        yield Label(
            str(self.__witness.rank) if self.__witness.rank is not None else "Outside top 105", classes="witness-rank"
        )
        yield Label(self.__witness.name, classes="witness-name")
        yield Label(str(self.__witness.votes), classes="witness-votes")
        yield Label("details", classes="witness-details")

    @on(WitnessCheckBoxChanged)
    def move_witness_to_actions(self) -> None:
        witnesses_actions = self.app.query_one(WitnessesActions)

        if self.__witness_checkbox.checkbox_state:
            witnesses_actions.mount_witness(name=self.__witness.name, vote=not self.__witness.voted)
            return
        witnesses_actions.unmount_witness(name=self.__witness.name)


class WitnessActionRow(Horizontal):
    def __init__(self, name: str, vote: bool):
        super().__init__(id=f"{name}-witness")
        self.__witness_name = name
        self.__vote = vote

    def compose(self) -> ComposeResult:
        if self.__vote:
            yield Label("Vote", classes="action-vote")
        else:
            yield Label("Unvote", classes="action-unvote")
        yield Label(self.__witness_name, classes="action-witness-name")


class WitnessesActions(VerticalScroll):
    """
    Contains a table of operations to be performed after confirmation.

    Attributes
    ----------
    __actions_to_perform (dict): A dictionary with the witness name as the key and the action to perform (vote/unvote, represented as a boolean value).
    """
    def __init__(self) -> None:
        super().__init__()
        self.__actions_to_perform: dict[str, bool] = {}

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="witnesses-actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-row")
            yield Static("Witness", id="witness-row")

    def mount_witness(self, name: str, vote: bool) -> None:
        self.mount(WitnessActionRow(name=name, vote=vote))
        self.__actions_to_perform[name] = vote

    def unmount_witness(self, name: str) -> None:
        self.query_one(f"#{name}-witness").remove()
        self.__actions_to_perform.pop(name)

    @property
    def actions_to_perform(self) -> dict[str, bool]:
        return self.__actions_to_perform


class WitnessesList(Vertical, CliveWidget):
    def __init__(self, witnesses: list[WitnessT] | None, first_witness_index: int) -> None:
        super().__init__()
        self.__witnesses = witnesses
        self.__first_witness_index = first_witness_index

    def compose(self) -> ComposeResult:
        if self.__witnesses is None:
            yield Static("Loading the list of witnesses")
        else:
            for witness in self.__witnesses[self.__first_witness_index : self.__first_witness_index + 15]:
                yield Witness(witness)
                yield Static()


class WitnessesListHeader(Grid):
    def compose(self) -> ComposeResult:
        yield Static()
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")
        yield Static()


class WitnessesTable(Vertical, CliveWidget):
    can_focus = True

    def __init__(self, witnesses: list[WitnessT] | None):
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


class Witnesses(ScrollableTabPane, MultiplyOperationsActionsBindings):
    """TabPane with all content about witnesses."""

    def __init__(self, provider: GovernanceDataProvider, title: TextType) -> None:
        super().__init__(title=title)
        self.__provider = provider

    def compose(self) -> ComposeResult:
        yield WitnessesActions()
        yield WitnessesTable(self.__provider.content.witnesses)

    def on_mount(self) -> None:
        self.watch(self.__provider, "content", callback=self.__sync_witnesses_list)

    def __sync_witnesses_list(self, content: GovernanceData) -> None:
        try:
            witnesses_list_container = self.query_one(WitnessesTable)
        except NoMatches:
            return

        witnesses_list_container.remove()
        new_witnesses_table_container = WitnessesTable(content.witnesses)
        self.mount(new_witnesses_table_container)

    def _create_operation(self) -> list[Operation] | None:
        working_account_name = self.app.world.profile_data.working_account.name
        operations_to_perform = self.app.query_one(WitnessesActions).actions_to_perform
        list_of_operations = []

        for witness, approve in operations_to_perform.items():
            if witness is None or approve is None:
                return None

            list_of_operations.append(
                AccountWitnessVoteOperation(account=working_account_name, witness=witness, approve=approve)
            )
        return list_of_operations  # type: ignore[return-value]


class Governance(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with GovernanceDataProvider() as provider, CliveTabbedContent():
            yield Proxy("Proxy")
            yield Witnesses(provider, "Witnesses")
            yield Proposals("Proposals")
