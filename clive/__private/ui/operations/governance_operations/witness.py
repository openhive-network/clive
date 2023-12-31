from __future__ import annotations

import contextlib
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from textual import on, work
from textual.binding import Binding
from textual.containers import Grid, Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Click, Enter
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static, TabPane

from clive.__private.config import settings
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.witnesses_data_provider import WitnessesDataProvider
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.operations.governance_operations.governance_checkbox import GovernanceCheckbox
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.witness_pattern_input import WitnessPatternInput
from schemas.operations.account_witness_vote_operation import AccountWitnessVoteOperation

if TYPE_CHECKING:
    from typing import Final

    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData
    from clive.models import Operation

MAX_NUMBER_OF_WITNESSES_VOTES: Final[int] = 30
MAX_NUMBER_OF_WITNESSES_IN_TABLE: Final[int] = 150
MAX_WITNESSES_ON_PAGE: Final[int] = 30


def convert_witness_name_to_widget_id(witness_name: str) -> str:
    return witness_name.replace(".", "")


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class DetailsLabel(Label):
    class Clicked(Message):
        """Message send when DetailsLabel is clicked."""

    def __init__(self, *, classes: str | None = None):
        super().__init__(renderable="details", classes=classes)

    @on(Click)
    def clicked(self) -> None:
        self.post_message(self.Clicked())


class WitnessDetailsWidget(Static):
    BORDER_TITLE = "WITNESS DETAILS"


class DetailsScreen(ModalScreen[None], CliveWidget):
    BINDINGS = [Binding("escape,f3", "request_quit", "Close")]

    def __init__(self, witness_name: str) -> None:
        super().__init__()
        self.__witness_name = witness_name

    def on_mount(self) -> None:
        self.set_interval(settings.get("node.refresh_rate", 1.5), lambda: self.refresh_witness_data())

    def compose(self) -> ComposeResult:
        widget = WitnessDetailsWidget()
        widget.loading = True
        yield widget

    @work(name="governance update modal details")
    async def refresh_witness_data(self) -> None:
        wrapper = await self.app.world.commands.find_witness(witness_name=self.__witness_name)
        await self.query("*").remove()

        if wrapper.error_occurred:
            new_witness_data = f"Unable to retrieve witness information:\n{wrapper.error}"
        else:
            witness = wrapper.result_or_raise
            url = witness.url
            created = humanize_datetime(witness.created)
            missed_blocks = witness.total_missed
            last_block = witness.last_confirmed_block_num
            price_feed = int(witness.hbd_exchange_rate.base.amount) / 10**3
            version = witness.running_version
            new_witness_data = f"""\
            === Time of the query: {humanize_datetime(datetime.now().replace(microsecond=0))} ===
                url: {url}
                created: {created}
                missed blocks: {missed_blocks}
                last block: {last_block}
                price feed: {price_feed} $
                version: {version}\
            """
        await self.mount(WitnessDetailsWidget(new_witness_data))

    def action_request_quit(self) -> None:
        self.app.pop_screen()

    @on(Click)
    def close_screen_by_click(self) -> None:
        self.app.pop_screen()


class WitnessNameLabel(Label, CliveWidget):
    """Created because textual is not responding `on(Enter)` in Witness Grid."""

    def __init__(self, witness_name: str, classes: str) -> None:
        super().__init__(
            renderable=witness_name,
            id=f"{convert_witness_name_to_widget_id(witness_name)}-witness-info",
            classes=classes,
        )
        self.__witness_name = witness_name

    @on(Enter)
    async def __update_tooltip_text(self) -> None:
        wrapper = await self.app.world.commands.find_witness(witness_name=self.__witness_name)

        if wrapper.error_occurred:
            new_tooltip_text = f"Unable to retrieve witness information:\n{wrapper.error}"
        else:
            witness = wrapper.result_or_raise
            created = humanize_datetime(witness.created)
            missed_blocks = witness.total_missed
            last_block = witness.last_confirmed_block_num
            price_feed = int(witness.hbd_exchange_rate.base.amount) / 10**3
            version = witness.running_version
            new_tooltip_text = f"""\
        created: {created}
        missed blocks: {missed_blocks}
        last block: {last_block}
        price feed: {price_feed} $
        version: {version}\
    """

        self.tooltip = new_tooltip_text


class Witness(Grid, CliveWidget, can_focus=True):
    """The class first checks if there is a witness in the action table - if so, move True to the WitnessCheckbox parameter."""

    BINDINGS = [
        Binding("f3", "show_details", "Details"),
        Binding("pageup", "previous_page", "PgDn"),
        Binding("pagedown", "next_page", "PgUp"),
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    def __init__(self, witness: WitnessData, evenness: str = "even") -> None:
        super().__init__()
        self.__witness = witness
        self.__evenness = evenness

        self.witness_checkbox = GovernanceCheckbox(
            is_voted=witness.voted,
            initial_state=self.is_witness_operation_in_cart or self.is_already_in_witness_actions_container,
            disabled=bool(self.app.world.profile_data.working_account.data.proxy) or self.is_witness_operation_in_cart,
        )

    def on_mount(self) -> None:
        self.watch(self.witness_checkbox, "disabled", callback=self.dimm_on_disabled_checkbox)

    def compose(self) -> ComposeResult:
        yield self.witness_checkbox
        yield Label(
            str(self.__witness.rank) if self.__witness.rank is not None else f">{MAX_NUMBER_OF_WITNESSES_IN_TABLE}",
            classes=f"witness-rank-{self.__evenness}",
        )
        yield WitnessNameLabel(
            self.__witness.name,
            classes=f"witness-name-{self.__evenness}",
        )
        yield Label(str(self.__witness.votes), classes=f"witness-votes-{self.__evenness}")
        yield DetailsLabel(classes=f"witness-details-{self.__evenness}")

    async def move_witness_to_actions(self) -> None:
        witnesses_actions = self.app.query_one(WitnessesActions)
        if self.witness_checkbox.value:
            await witnesses_actions.mount_witness(name=self.__witness.name, vote=not self.__witness.voted)
            return
        await witnesses_actions.unmount_witness(name=self.__witness.name, vote=not self.__witness.voted)

    def dimm_on_disabled_checkbox(self, value: bool) -> None:
        if value:
            self.add_class("dimmed")
            return
        self.remove_class("dimmed")

    @on(GovernanceCheckbox.Clicked)
    def focus_myself(self) -> None:
        self.focus()

    @on(GovernanceCheckbox.Changed)
    async def modify_action_status(self) -> None:
        await self.move_witness_to_actions()

    @on(DetailsLabel.Clicked)
    async def action_show_details(self) -> None:
        await self.app.push_screen(DetailsScreen(witness_name=self.__witness.name))

    async def action_next_page(self) -> None:
        await self.app.query_one(WitnessesTable).next_page()

    async def action_previous_page(self) -> None:
        await self.app.query_one(WitnessesTable).previous_page()

    def action_toggle_checkbox(self) -> None:
        self.witness_checkbox.toggle()

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
    @dataclass
    class Search(Message):
        """Emitted when the search button is pressed."""

        pattern: str
        limit: int

    class Clear(Message):
        """Emitted when the search input is cleared."""

    def __init__(self) -> None:
        super().__init__()

        self.__witness_input = WitnessPatternInput(id_="witness-pattern-input")
        self.__limit_input = IntegerInput(label="limit", id_="limit-input", placeholder="default - 150")

        self.__limit_just_input: Input
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
        pattern = self.__witness_input.value

        try:
            limit = int(self.__limit_just_input.value)
        except ValueError:
            limit = MAX_NUMBER_OF_WITNESSES_IN_TABLE

        if pattern is None or limit is None:
            return

        self.post_message(self.Search(pattern, limit))

    @on(CliveButton.Pressed, "#clear-custom-witnesses-button")
    def clear_searched_witnesses(self) -> None:
        self.__witness_input.input.clear()
        self.__limit_just_input.clear()
        self.post_message(self.Clear())


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


class WitnessesActions(VerticalScroll, CanFocusWithScrollbarsOnly):
    """
    Contains a table of operations to be performed after confirmation.

    Attributes
    ----------
    __actions_to_perform (dict): A dictionary with the witness name as the key and the action to perform (vote/unvote, represented as a boolean value).
    """

    def __init__(self) -> None:
        super().__init__()
        self.__actions_to_perform: dict[str, bool] = {}

        self.__actions_votes = 0

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="witnesses-actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-row")
            yield Static("Witness", id="witness-row")

    async def on_mount(self) -> None:  # type: ignore[override]
        for operation in self.app.world.profile_data.cart:
            if isinstance(operation, AccountWitnessVoteOperation):
                await self.mount_witness(name=operation.witness, vote=operation.approve, pending=True)

    async def mount_witness(self, name: str, vote: bool, pending: bool = False) -> None:
        # check if witness is already in the list, if so - return
        with contextlib.suppress(NoMatches):
            self.query_one(self.get_witness_action_row(name))
            return

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
        try:
            await self.query_one(self.get_witness_action_row(name)).remove()
        except NoMatches:
            return

        if vote:
            self.__actions_votes -= 1
        else:
            self.__actions_votes += 1

        self.__actions_to_perform.pop(name)

    @staticmethod
    def get_witness_action_row(name: str) -> str:
        return f"#{convert_witness_name_to_widget_id(name)}-witness-action-row"

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.app.query_one(WitnessesDataProvider)

    @property
    def actions_to_perform(self) -> dict[str, bool]:
        return self.__actions_to_perform

    @property
    def actual_number_of_votes(self) -> int:
        return self.provider.content.number_of_votes + self.__actions_votes


class WitnessesList(Vertical, CliveWidget):
    def __init__(
        self,
        witnesses: list[WitnessData] | None,
    ) -> None:
        super().__init__()
        self.__witnesses_to_display = witnesses if witnesses is not None else None

    def compose(self) -> ComposeResult:
        if not self.__witnesses_to_display:
            self.loading = True
            return

        for id_, witness in enumerate(self.__witnesses_to_display):
            if id_ % 2 == 0:
                yield Witness(witness)
            else:
                yield Witness(witness, evenness="odd")


class ArrowUpWidget(Static):
    def __init__(self) -> None:
        super().__init__(renderable="↑ PgUp")

    @on(Click)
    async def previous_page(self) -> None:
        await self.app.query_one(WitnessesTable).previous_page()


class ArrowDownWidget(Static):
    def __init__(self) -> None:
        super().__init__(renderable="↓ PgDn")

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
    def __init__(self) -> None:
        super().__init__()
        self.__witness_index = 0

        self.__header = WitnessesListHeader()
        self.__is_loading = True

    def compose(self) -> ComposeResult:
        yield Static("Modify the votes for witnesses", id="witnesses-headline")
        yield self.__header
        yield WitnessesList(self.witnesses_chunk)

    async def __set_loading(self) -> None:
        self.__is_loading = True
        with contextlib.suppress(NoMatches):
            witness_list = self.query_one(WitnessesList)
            await witness_list.query("*").remove()
            await witness_list.mount(Label("Loading..."))

    def __set_loaded(self) -> None:
        self.__is_loading = False

    async def search_witnesses(self, pattern: str, limit: int) -> None:
        await self.provider.set_mode_witnesses_by_name(pattern=pattern, limit=limit).wait()
        await self.reset_page()

    async def clear_searched_witnesses(self) -> None:
        await self.provider.set_mode_top_witnesses().wait()
        await self.reset_page()

    async def reset_page(self) -> None:
        """During reset we cannot call __sync_witness_list because we have to wait for the provider to update the data."""
        self.__witness_index = 0
        self.__header.arrow_up.visible = False
        self.__header.arrow_down.visible = True

        if not self.__is_loading:
            await self.__sync_witnesses_list()

    async def next_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user from switching to an empty page by key binding
        if self.amount_of_fetched_witnesses - MAX_WITNESSES_ON_PAGE <= self.__witness_index + 1:
            self.notify("No witnesses on the next page", severity="warning")
            return

        self.__witness_index += MAX_WITNESSES_ON_PAGE

        self.__header.arrow_up.visible = True

        if self.amount_of_fetched_witnesses - MAX_WITNESSES_ON_PAGE <= self.__witness_index:
            self.__header.arrow_down.visible = False

        await self.__sync_witnesses_list(focus_first_witness=True)

    async def previous_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user going to a page with a negative index by key binding
        if self.__witness_index <= 0:
            self.notify("No witnesses on the previous page", severity="warning")
            return

        self.__header.arrow_down.visible = True

        self.__witness_index -= 30

        if self.__witness_index <= 0:
            self.__header.arrow_up.visible = False

        await self.__sync_witnesses_list(focus_first_witness=True)

    def on_mount(self) -> None:
        self.watch(self.provider, "content", callback=lambda: self.__sync_witnesses_list())

    async def __sync_witnesses_list(self, focus_first_witness: bool = False) -> None:
        await self.__set_loading()

        new_witnesses_list = WitnessesList(self.witnesses_chunk)

        with self.app.batch_update():
            await self.query(WitnessesList).remove()
            await self.mount(new_witnesses_list)

        if focus_first_witness:
            first_witness = self.query(Witness).first()
            first_witness.focus()

        self.__set_loaded()

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.app.query_one(WitnessesDataProvider)

    @property
    def amount_of_fetched_witnesses(self) -> int:
        return len(self.provider.content.witnesses)

    @property
    def witnesses_chunk(self) -> list[WitnessData] | None:
        if self.provider.content.witnesses is None:
            return None
        return list(self.provider.content.witnesses.values())[
            self.__witness_index : self.__witness_index + MAX_WITNESSES_ON_PAGE
        ]


class Witnesses(TabPane, OperationActionBindings):
    """TabPane with all content about witnesses."""

    def __init__(self, title: TextType) -> None:
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        self.__witness_table = WitnessesTable()

        with ScrollablePart(), Horizontal(id="witness-vote-actions"):
            yield self.__witness_table
            yield WitnessesActions()
        yield WitnessManualSearch()

    def _create_operations(self) -> list[Operation] | None:
        actual_number_of_votes = self.app.query_one(WitnessesActions).actual_number_of_votes

        if actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify(
                f"The number of voted witnesses may not exceed {MAX_NUMBER_OF_WITNESSES_VOTES}!", severity="error"
            )
            return None

        working_account_name = self.app.world.profile_data.working_account.name
        operations_to_perform = self.app.query_one(WitnessesActions).actions_to_perform

        return [
            AccountWitnessVoteOperation(account=working_account_name, witness=witness, approve=approve)
            for witness, approve in operations_to_perform.items()
        ]

    @on(WitnessManualSearch.Search)
    async def search_witnesses(self, message: WitnessManualSearch.Search) -> None:
        await self.__witness_table.search_witnesses(pattern=message.pattern, limit=message.limit)

    @on(WitnessManualSearch.Clear)
    async def clear_searched_witnesses(self, _: WitnessManualSearch.Clear) -> None:
        await self.__witness_table.clear_searched_witnesses()
