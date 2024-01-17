from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

from textual import on, work
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.events import Click, Enter
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

from clive.__private.config import settings
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.ui.data_providers.witnesses_data_provider import WitnessesDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.governance_operations.common_governance.common_elements import (
    GovernanceActionRow,
    GovernanceActions,
    GovernanceListHeader,
    GovernanceListWidget,
    GovernanceTable,
    GovernanceTableRow,
    GovernanceTabPane,
    ScrollablePart,
)
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.witness_pattern_input import WitnessPatternInput
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


class Witness(GovernanceTableRow[WitnessData]):
    """The class first checks if there is a witness in the action table - if so, move True to the WitnessCheckbox parameter."""

    BINDINGS = [Binding("f3", "show_details", "Details")]

    def create_row_content(self) -> ComposeResult:
        yield Label(
            str(self.row_data.rank) if self.row_data.rank is not None else f">{MAX_NUMBER_OF_WITNESSES_IN_TABLE}",
            classes=f"witness-rank-{self.evenness}",
        )
        yield WitnessNameLabel(
            self.row_data.name,
            classes=f"witness-name-{self.evenness}",
        )
        yield Label(str(self.row_data.votes), classes=f"witness-votes-{self.evenness}")
        yield DetailsLabel(classes=f"witness-details-{self.evenness}")

    @on(DetailsLabel.Clicked)
    async def action_show_details(self) -> None:
        await self.app.push_screen(DetailsScreen(witness_name=self.row_data.name))

    @property
    def action_identifier(self) -> str:
        return self.row_data.name

    @property
    def is_operation_in_cart(self) -> bool:
        return (
            AccountWitnessVoteOperation(
                account=self.app.world.profile_data.working_account.name,
                witness=self.row_data.name,
                approve=not self.row_data.voted,
            )
            in self.app.world.profile_data.cart
        )

    @property
    def is_already_in_actions_container(self) -> bool:
        try:
            self.app.query_one(WitnessesActions.get_action_id(self.row_data.name))
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


class WitnessActionRow(GovernanceActionRow):
    def create_widget_id(self) -> str:
        return f"{convert_witness_name_to_widget_id(self.action_identifier)}-witness-action-row"


class WitnessesActions(GovernanceActions):
    NAME_OF_ACTION: ClassVar[str] = "Witness"

    async def mount_operations_from_cart(self) -> None:
        for operation in self.app.world.profile_data.cart:
            if isinstance(operation, AccountWitnessVoteOperation):
                await self.add_row(identifier=operation.witness, vote=operation.approve, pending=True)

    @staticmethod
    def get_action_id(identifier: str) -> str:
        return f"#{convert_witness_name_to_widget_id(identifier)}-witness-action-row"

    def create_action_row(self, identifier: str, vote: bool, pending: bool) -> GovernanceActionRow:
        return WitnessActionRow(identifier, vote, pending)

    def create_number_of_votes_restriction(self) -> None:
        if self.actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify(f"The number of voted witnesses may not exceed {MAX_NUMBER_OF_WITNESSES_VOTES}")

    @property
    def actual_number_of_votes(self) -> int:
        return self.provider.content.number_of_votes + self.actions_votes

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.app.query_one(WitnessesDataProvider)


class WitnessesList(GovernanceListWidget[WitnessData]):
    def _create_row(self, data: WitnessData, *, even: bool = False) -> Witness:
        return Witness(data, even=even)


class WitnessesListHeader(GovernanceListHeader):
    def create_custom_columns(self) -> ComposeResult:
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")

    def create_additional_headlines(self) -> ComposeResult:
        yield Static("Modify the votes for witnesses", id="witnesses-additional-headline")


class WitnessesTable(GovernanceTable[WitnessData, WitnessesDataProvider]):
    MAX_ELEMENTS_ON_PAGE: ClassVar[int] = 30

    async def search_witnesses(self, pattern: str, limit: int) -> None:
        await self.provider.set_mode_witnesses_by_name(pattern=pattern, limit=limit).wait()
        await self.reset_page()

    async def clear_searched_witnesses(self) -> None:
        await self.provider.set_mode_top_witnesses().wait()
        await self.reset_page()

    def create_new_list_widget(self) -> WitnessesList:
        return WitnessesList(self.data_chunk)

    def create_header(self) -> GovernanceListHeader:
        return WitnessesListHeader()

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.app.query_one(WitnessesDataProvider)

    @property
    def data(self) -> list[WitnessData]:
        return list(self.provider.content.witnesses.values())


class Witnesses(GovernanceTabPane):
    """TabPane with all content about witnesses."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType) -> None:
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        self.__witness_table = WitnessesTable()

        with ScrollablePart(), Horizontal(classes="vote-actions"):
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
