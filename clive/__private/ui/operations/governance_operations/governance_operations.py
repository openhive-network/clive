from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Click
from textual.widgets import Input, Label, LoadingIndicator, Static

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.bindings.multiply_operation_actions_bindings import MultiplyOperationsActionsBindings
from clive.__private.ui.operations.governance_operations.governance_data import GovernanceDataProvider
from clive.__private.ui.operations.governance_operations.governance_data import Witness as WitnessInformation
from clive.__private.ui.operations.governance_operations.witness_checkbox import (
    WitnessCheckbox,
    WitnessCheckBoxChanged,
)
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.witness_pattern_input import WitnessPatternInput
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane
from schemas.operations.account_witness_vote_operation import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from typing import Final

    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.models import Operation

MAX_NUMBER_OF_WITNESSES_VOTES: Final[int] = 30
MAX_NUMBER_OF_WITNESSES_IN_TABLE: Final[int] = 150


def convert_witness_name_to_widget_id(witness_name: str) -> str:
    return witness_name.replace(".", "")


class DetailsLabel(Label):
    def __init__(self, related_witness: Witness, classes: str):
        super().__init__(renderable="details", classes=classes)
        self.__related_witness = related_witness

    @on(Click)
    def show_witness_details(self) -> None:
        self.__related_witness.action_show_details()


class WitnessDetails(Vertical):
    def __init__(self, witness: WitnessInformation):
        super().__init__()
        self.__witness = witness

    def compose(self) -> ComposeResult:
        yield Static(f"witness: {self.__witness.name}")
        yield Static(f"url: {self.__witness.url}")
        yield Static(f"created: {humanize_datetime(self.__witness.created)}")
        yield Static(f"missed blocks: {self.__witness.missed_blocks}")
        yield Static(f"last block: {self.__witness.last_block}")
        yield Static(f"price feed: {self.__witness.price_feed}")
        yield Static(f"version: {self.__witness.version}")


class Witness(Grid, CliveWidget, can_focus=True):
    """The class first checks if there is a witness in the action table - if so, move True to the WitnessCheckbox parameter."""

    BINDINGS = [
        Binding("f3", "show_details", "Details"),
        Binding("pageup", "previous_page", "PgDn"),
        Binding("pagedown", "next_page", "PgUp"),
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    def __init__(self, witness: WitnessInformation, evenness: str = "even") -> None:
        super().__init__()
        self.__witness = witness
        self.__evenness = evenness

        self.disabled = self.is_witness_operation_in_cart

        self.witness_checkbox = WitnessCheckbox(
            related_witness=self,
            classes="witness-checkbox",
            is_voted=witness.voted,
            initial_state=self.is_witness_operation_in_cart or self.is_already_in_witness_actions_container,
        )

    def compose(self) -> ComposeResult:
        yield self.witness_checkbox
        yield Label(
            str(self.__witness.rank) if self.__witness.rank is not None else f">{MAX_NUMBER_OF_WITNESSES_IN_TABLE}",
            classes=f"witness-rank-{self.__evenness}",
        )
        yield Label(
            self.__witness.name,
            classes=f"witness-name-{self.__evenness}",
            id=f"{convert_witness_name_to_widget_id(self.__witness.name)}-witness-info",
        )
        yield Label(str(self.__witness.votes), classes=f"witness-votes-{self.__evenness}")
        yield DetailsLabel(related_witness=self, classes=f"witness-details-{self.__evenness}")

    def on_mount(self) -> None:
        tooltip_text = f"""
        {f"created: {humanize_datetime(self.__witness.created)}"}
        {f"missed blocks: {self.__witness.missed_blocks}"}
        {f"last block: {self.__witness.last_block}"}
        {f"price feed: {self.__witness.price_feed}"}
        {f"version: {self.__witness.version}"}
        """
        self.query_one(f"#{convert_witness_name_to_widget_id(self.__witness.name)}-witness-info").tooltip = tooltip_text

    @on(WitnessCheckBoxChanged)
    async def move_witness_to_actions(self) -> None:
        with self.app.batch_update():
            witnesses_actions = self.app.query_one(WitnessesActions)
            if self.witness_checkbox.checkbox_state:
                await witnesses_actions.mount_witness(name=self.__witness.name, vote=not self.__witness.voted)
                return
            await witnesses_actions.unmount_witness(name=self.__witness.name, vote=not self.__witness.voted)

    def action_show_details(self) -> None:
        try:
            self.app.query_one(WitnessDetails).remove()
        except NoMatches:
            self.app.query_one(WitnessesList).mount(WitnessDetails(self.__witness))

    async def action_next_page(self) -> None:
        await self.app.query_one(WitnessesTable).next_page()

    async def action_previous_page(self) -> None:
        await self.app.query_one(WitnessesTable).previous_page()

    def action_toggle_checkbox(self) -> None:
        self.witness_checkbox.press()

    @property
    def is_witness_operation_in_cart(self) -> bool:
        return (
            AccountWitnessVoteOperation(
                account=self.app.world.profile_data.working_account.name,
                witness=self.__witness.name,
                approve=not self.__witness.voted,
            )
            in self.app.world.profile_data.cart
        )

    @property
    def is_already_in_witness_actions_container(self) -> bool:
        try:
            self.app.query_one(WitnessesActions.get_witness_action_row(self.__witness.name))
        except NoMatches:
            return False
        else:
            return True


class WitnessManualSearch(Horizontal):
    def __init__(self) -> None:
        super().__init__()
        self.__witness_input = WitnessPatternInput(id_="witness-pattern-input")
        self.__limit_input = IntegerInput(label="limit", id_="limit-input", placeholder="default - 150")

        self.__limit_just_input: Input = Input()
        self.__limit_just_label, self.__limit_just_input = self.__limit_input.compose()  # type: ignore[assignment]
        self.__witness_just_label, self.__witness_just_input = self.__witness_input.compose()

    def compose(self) -> ComposeResult:
        with Horizontal(id="inputs-with-statics-manual"):
            with Vertical(id="witness-pattern-input-with-label"):
                yield self.__witness_just_label
                yield self.__witness_just_input
            with Vertical(id="witness-input-limit-with-label"):
                yield self.__limit_just_label
                yield self.__limit_just_input

        with Horizontal(id="search-and-clear-buttons"):
            yield CliveButton("Search", id_="witness-search-button")
            yield CliveButton("Clear", id_="clear-custom-witnesses-button")

    @on(CliveButton.Pressed, "#witness-search-button")
    def search_witnesses(self) -> None:
        provider = self.app.query_one(GovernanceDataProvider)
        value_from_pattern_input = self.__witness_input.value

        try:
            value_from_limit_input = int(self.__limit_just_input.value)
        except ValueError:
            value_from_limit_input = MAX_NUMBER_OF_WITNESSES_IN_TABLE

        if value_from_pattern_input is None and value_from_limit_input is None:
            return

        provider.order_by_name = True
        provider.witness_pattern_to_search = value_from_pattern_input  # type:ignore[assignment]
        provider.limit = value_from_limit_input
        provider.pause_refreshing_data()
        return

    @on(CliveButton.Pressed, "#clear-custom-witnesses-button")
    def clear_searched_witnesses(self) -> None:
        provider = self.app.query_one(GovernanceDataProvider)

        provider.order_by_name = False
        provider.resume_refreshing_data()
        self.__witness_input.input.value = ""
        self.__limit_just_input.value = ""


class WitnessActionRow(Horizontal):
    def __init__(self, name: str, vote: bool, pending: bool = False):
        super().__init__(id=f"{convert_witness_name_to_widget_id(name)}-witness-action-row")
        self.__witness_name = name
        self.__vote = vote
        self.__pending = pending

    def compose(self) -> ComposeResult:
        if self.__pending:
            yield Label("Pending", classes="action-pending action-label")
            yield Label(self.__witness_name, classes="action-witness-name")
            return

        if self.__vote:
            yield Label("Vote", classes="action-vote action-label")
        else:
            yield Label("Unvote", classes="action-unvote action-label")
        yield Label(self.__witness_name, classes="action-witness-name")


class WitnessesActions(VerticalScroll, CliveWidget):
    """
    Contains a table of operations to be performed after confirmation.

    Attributes
    ----------
    __actions_to_perform (dict): A dictionary with the witness name as the key and the action to perform (vote/unvote, represented as a boolean value).
    """

    def __init__(self) -> None:
        super().__init__()
        self.__actions_to_perform: dict[str, bool] = {}

        self.__provider = self.app.query_one(GovernanceDataProvider)
        self.__actions_votes = 0

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="witnesses-actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-row")
            yield Static("Witness", id="witness-row")

    async def on_mount(self) -> None:
        for operation in self.app.world.profile_data.cart:
            if isinstance(operation, AccountWitnessVoteOperation):
                await self.mount_witness(name=operation.witness, vote=operation.approve, pending=True)

    async def mount_witness(self, name: str, vote: bool, pending: bool = False) -> None:
        await self.mount(WitnessActionRow(name=name, vote=vote, pending=pending))

        if vote:
            self.__actions_votes += 1
        else:
            self.__actions_votes -= 1

        if self.actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify(f"The number of voted witnesses may not exceed {MAX_NUMBER_OF_WITNESSES_VOTES}")

        if not pending:
            self.__actions_to_perform[name] = vote

    async def unmount_witness(self, name: str, vote: bool) -> None:
        await self.query_one(self.get_witness_action_row(name)).remove()

        if vote:
            self.__actions_votes -= 1
        else:
            self.__actions_votes += 1

    @staticmethod
    def get_witness_action_row(name: str) -> str:
        return f"#{convert_witness_name_to_widget_id(name)}-witness-action-row"

    @property
    def actions_to_perform(self) -> dict[str, bool]:
        return self.__actions_to_perform

    @property
    def actual_number_of_votes(self) -> int:
        return self.__provider.content.number_of_votes + self.__actions_votes


class WitnessesList(Vertical, CliveWidget):
    def __init__(
        self,
        witnesses: list[WitnessInformation] | None,
    ) -> None:
        super().__init__()
        self.__witnesses_to_display = witnesses if witnesses is not None else None

    def compose(self) -> ComposeResult:
        if self.__witnesses_to_display is None:
            yield LoadingIndicator()
        else:
            for id_, witness in enumerate(self.__witnesses_to_display):
                if id_ % 2 == 0:
                    yield Witness(witness)
                else:
                    yield Witness(witness, evenness="odd")


class ArrowUpWidget(Static):
    def __init__(self) -> None:
        super().__init__(renderable="↑")

    @on(Click)
    async def previous_page(self) -> None:
        await self.app.query_one(WitnessesTable).previous_page()


class ArrowDownWidget(Static):
    def __init__(self) -> None:
        super().__init__(renderable="↓")

    @on(Click)
    async def next_page(self) -> None:
        await self.app.query_one(WitnessesTable).next_page()


class WitnessesListHeader(Grid):
    def __init__(self) -> None:
        super().__init__()
        self.arrow_up = ArrowUpWidget()
        self.arrow_down = ArrowDownWidget()

        self.arrow_up.visible = False

    def compose(self) -> ComposeResult:
        yield self.arrow_up
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")
        yield self.arrow_down


class WitnessesTable(Vertical, CliveWidget, can_focus=False):
    def __init__(self, provider: GovernanceDataProvider):
        super().__init__()
        self.__provider = provider
        self.__witness_index = 0

        self.__header = WitnessesListHeader()

    def compose(self) -> ComposeResult:
        yield Static("Modify the votes for witnesses", id="witnesses-headline")
        yield self.__header
        yield WitnessesList(self.witnesses_chunk)

    async def next_page(self) -> None:
        self.__header.arrow_up.visible = True
        last_possible_index = 120
        if self.__witness_index >= last_possible_index:
            self.notify(
                f"Just {MAX_NUMBER_OF_WITNESSES_IN_TABLE} witnesses are available, please type witness outside the list"
                " and search below"
            )
            return

        with self.app.batch_update():
            await self.query_one(WitnessesList).remove()
            self.__witness_index += 30
            if self.__witness_index >= last_possible_index:
                self.__header.arrow_down.visible = False

            next_witnesses_page = WitnessesList(self.witnesses_chunk)
            await self.mount(next_witnesses_page)
            first_witness = self.app.query(Witness).first()
            self.app.set_focus(first_witness)

    async def previous_page(self) -> None:
        self.__header.arrow_down.visible = True

        if self.__witness_index <= 0:
            self.notify("Cannot go up, no witness above")
            return

        with self.app.batch_update():
            await self.query_one(WitnessesList).remove()
            self.__witness_index -= 30
            if self.__witness_index <= 0:
                self.__header.arrow_up.visible = False
            next_witnesses_page = WitnessesList(self.witnesses_chunk)
            await self.mount(next_witnesses_page)
            first_witness = self.app.query(Witness).first()
            self.app.set_focus(first_witness)

    def on_mount(self) -> None:
        self.watch(self.__provider, "content", callback=self.__sync_witnesses_list)

    def __sync_witnesses_list(self) -> None:
        try:
            self.query_one(WitnessesList).remove()
        except NoMatches:
            return
        new_witnesses_list_container = WitnessesList(self.witnesses_chunk)
        self.mount(new_witnesses_list_container)

    @property
    def witnesses_list(self) -> dict[str, WitnessInformation] | None:
        return self.__provider.content.witnesses

    @property
    def witnesses_chunk(self) -> list[WitnessData] | None:
        if self.__provider.content.witnesses is None:
            return None
        return list(self.__provider.content.witnesses.values())[self.__witness_index : self.__witness_index + 30]


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
        with Horizontal(id="witness-vote-actions"):
            yield WitnessesTable(self.__provider)
            yield WitnessesActions()
        yield WitnessManualSearch()

    def _create_operation(self) -> list[Operation] | None:
        actual_number_of_votes = self.app.query_one(WitnessesActions).actual_number_of_votes

        if actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify("The number of voted witnesses may not exceed 30 !", severity="error")
            return None

        working_account_name = self.app.world.profile_data.working_account.name
        operations_to_perform = self.app.query_one(WitnessesActions).actions_to_perform

        return [
            AccountWitnessVoteOperation(account=working_account_name, witness=witness, approve=approve)
            for witness, approve in operations_to_perform.items()
        ]


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