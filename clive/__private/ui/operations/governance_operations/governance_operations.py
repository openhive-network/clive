from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual._node_list import DuplicateIds
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Label, Static

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings.multiply_operation_actions_bindings import MultiplyOperationsActionsBindings
from clive.__private.ui.operations.governance_operations.governance_data import GovernanceDataProvider
from clive.__private.ui.operations.governance_operations.governance_data import Witness as WitnessInformation
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.witness_input import WitnessInput
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from clive.__private.ui.widgets.witness_checkbox import WitnessCheckbox, WitnessCheckBoxChanged
from schemas.operations.account_witness_vote_operation import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.models import Operation


class Witness(Grid):
    """The class first checks if there is a witness in the action table - if so, move True to the WitnessCheckbox parameter."""

    def __init__(self, witness: WitnessInformation, evenness: str = "even") -> None:
        super().__init__(id=f"{''.join(witness.name.split('.'))}-grid-container")
        self.__witness = witness
        self.__evenness = evenness

        try:
            self.app.query_one(f"#{''.join(witness.name.split('.'))}-witness")
        except NoMatches:
            self.witness_checkbox = WitnessCheckbox(is_voted=witness.voted)
        else:
            self.witness_checkbox = WitnessCheckbox(is_voted=witness.voted, initial_state=True)

    def compose(self) -> ComposeResult:
        yield self.witness_checkbox
        yield Label(
            str(self.__witness.rank) if self.__witness.rank is not None else "?",
            classes=f"witness-rank-{self.__evenness}",
        )
        yield Label(
            self.__witness.name,
            classes=f"witness-name-{self.__evenness}",
            id=f"{''.join(self.__witness.name.split('.'))}-witness-info",
        )
        yield Label(str(self.__witness.votes), classes=f"witness-votes-{self.__evenness}")
        yield Label("details", classes=f"witness-details-{self.__evenness}")

    def on_mount(self) -> None:
        tooltip_text = f"""
        {f"created: {humanize_datetime(self.__witness.created)}"}
        {f"missed blocks: {self.__witness.missed_blocks}"}
        {f"last block: {self.__witness.last_block}"}
        {f"price feed: {self.__witness.price_feed}"}
        {f"version: {self.__witness.version}"}
        """
        self.query_one(f"#{''.join(self.__witness.name.split('.'))}-witness-info").tooltip = tooltip_text

    @on(WitnessCheckBoxChanged)
    def move_witness_to_actions(self) -> None:
        witnesses_actions = self.app.query_one(WitnessesActions)

        if self.witness_checkbox.checkbox_state:
            witnesses_actions.mount_witness(name=self.__witness.name, vote=not self.__witness.voted)
            return
        witnesses_actions.unmount_witness(name=self.__witness.name)


class WitnessManualVote(Vertical):
    def __init__(self) -> None:
        super().__init__()
        self.__witness_input = WitnessInput()

    def compose(self) -> ComposeResult:
        yield Static("Can't find a witness ? Type and search !")
        yield self.__witness_input
        with Horizontal(id="search-and-clear-buttons"):
            yield CliveButton("Search", id_="witness-search-button")
            yield CliveButton("Clear", id_="clear-custom-witnesses-button")

    @on(Button.Pressed)
    def modify_actions_list(self, event: Button.Pressed) -> None:
        witnesses_table = self.app.query_one(WitnessesTable)

        if event.button.id == "witness-search-button":
            try:
                witness = WitnessInformation(name=self.__witness_input.value)

                if witnesses_table.witnesses_list is not None and witness in witnesses_table.witnesses_list:
                    self.app.query_one(f"#{''.join(witness.name.split('.'))}-grid-container").witness_checkbox.click()  # type: ignore[attr-defined]
                else:
                    witnesses_table.custom_witnesses_list.append(witness)
                    witnesses_table.custom_witnesses_changed = not witnesses_table.custom_witnesses_changed
                    return

            except DuplicateIds:
                self.notify("Witness is already in actions !", severity="error")

        if event.button.id == "clear-custom-witnesses-button":
            witnesses_table.custom_witnesses_list.clear()
            witnesses_table.custom_witnesses_changed = not witnesses_table.custom_witnesses_changed


class WitnessActionRow(Horizontal):
    def __init__(self, name: str, vote: bool):
        super().__init__(id=f"{''.join(name.split('.'))}-witness")
        self.__witness_name = name
        self.__vote = vote

    def compose(self) -> ComposeResult:
        if self.__vote:
            yield Label("Vote", classes="action-vote action-label")
        else:
            yield Label("Unvote", classes="action-unvote action-label")
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
        self.query_one(f"#{''.join(name.split('.'))}-witness").remove()
        self.__actions_to_perform.pop(name)

    @property
    def actions_to_perform(self) -> dict[str, bool]:
        return self.__actions_to_perform


class WitnessesList(Vertical, CliveWidget):
    def __init__(
        self,
        witnesses: list[WitnessInformation] | None,
        first_witness_index: int,
        custom_witnesses: list[WitnessInformation] | None = None,
    ) -> None:
        super().__init__()
        self.__first_witness_index = first_witness_index
        self.__witnesses_to_display = witnesses.copy() if witnesses is not None else None

        if custom_witnesses is not None and self.__witnesses_to_display is not None:
            for witness in custom_witnesses:
                if witness not in self.__witnesses_to_display:
                    self.__witnesses_to_display.insert(0, witness)

    def compose(self) -> ComposeResult:
        if self.__witnesses_to_display is None:
            yield Static("Loading the list of witnesses")
        else:
            for id_, witness in enumerate(
                self.__witnesses_to_display[self.__first_witness_index : self.__first_witness_index + 25]
            ):
                if id_ % 2 == 0:
                    yield Witness(witness)
                else:
                    yield Witness(witness, evenness="odd")


class WitnessesListHeader(Grid):
    def compose(self) -> ComposeResult:
        yield Static()
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")
        yield Static()


class WitnessesTable(Vertical, CliveWidget):
    can_focus = True
    custom_witnesses_changed: bool = var(False)  # type: ignore[assignment]
    """User also can put Witness by input - var to detect this"""

    def __init__(self, provider: GovernanceDataProvider):
        super().__init__()
        self.__provider = provider
        self.__witness_index = 0

        self.custom_witnesses_list: list[WitnessInformation] = []

    def compose(self) -> ComposeResult:
        yield Static("Modify the votes for witnesses", id="witnesses-headline")
        yield WitnessesListHeader()
        yield WitnessesList(self.__provider.content.witnesses, self.__witness_index, self.custom_witnesses_list)

    def on_focus(self) -> None:
        self.bind(Binding("left", "previous_page", "previous page"))
        self.bind(Binding("right", "next_page", "next page"))

    def action_next_page(self) -> None:
        last_possible_index = 175
        if self.__witness_index == last_possible_index:
            self.notify("Just 200 witnesses are available, please type witness outside the list and vote beside")
            return

        self.query_one(WitnessesList).remove()
        self.__witness_index += 25
        next_witnesses_page = WitnessesList(
            self.__provider.content.witnesses, self.__witness_index, self.custom_witnesses_list
        )
        self.mount(next_witnesses_page)
        return

    def action_previous_page(self) -> None:
        if self.__witness_index == 0:
            self.notify("Cannot switch to previous page")
            return

        self.query_one(WitnessesList).remove()
        self.__witness_index -= 25
        next_witnesses_page = WitnessesList(
            self.__provider.content.witnesses, self.__witness_index, self.custom_witnesses_list
        )
        self.mount(next_witnesses_page)
        return

    def on_mount(self) -> None:
        self.watch(self.__provider, "content", callback=self.__sync_witnesses_list)
        self.watch(self, "custom_witnesses_changed", callback=self.__sync_witnesses_list)

    def __sync_witnesses_list(self) -> None:
        try:
            self.query_one(WitnessesList).remove()
        except NoMatches:
            return
        new_witnesses_list_container = WitnessesList(
            self.__provider.content.witnesses, self.__witness_index, self.custom_witnesses_list
        )
        self.mount(new_witnesses_list_container)

    @property
    def witnesses_list(self) -> list[WitnessInformation] | None:
        return self.__provider.content.witnesses


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
        with Vertical(id="witness-vote-actions"):
            yield WitnessesTable(self.__provider)
            yield WitnessManualVote()
        yield WitnessesActions()

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
