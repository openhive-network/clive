from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Horizontal
from textual.events import Click, Enter
from textual.message import Message
from textual.validation import Integer
from textual.widgets import Label, Static

from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData, WitnessesDataRetrieval
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_hbd_exchange_rate
from clive.__private.ui.data_providers.witnesses_data_provider import WitnessesDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActionRow,
    GovernanceActions,
)
from clive.__private.ui.operations.governance_operations.common_governance.governance_tab_pane import (
    GovernanceTabPane,
)
from clive.__private.ui.operations.governance_operations.common_governance.governance_table import (
    GovernanceListHeader,
    GovernanceListWidget,
    GovernanceTable,
    GovernanceTableRow,
)
from clive.__private.ui.operations.governance_operations.witness.witness_details_screen import (
    WitnessDetailsScreen,
)
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_pattern_input import AccountNamePatternInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle
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


class WitnessDetailsLabel(Label):
    class Clicked(Message):
        """Message send when DetailsLabel is clicked."""

    def __init__(self, *, classes: str | None = None):
        super().__init__(renderable="details", classes=classes)

    @on(Click)
    def clicked(self) -> None:
        self.post_message(self.Clicked())


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
            price_feed = humanize_hbd_exchange_rate(witness.hbd_exchange_rate)
            version = witness.running_version
            new_tooltip_text = f"""\
        created: {created}
        missed blocks: {missed_blocks}
        last block: {last_block}
        price feed: {price_feed}
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
        yield WitnessDetailsLabel(classes=f"witness-details-{self.evenness}")

    @on(WitnessDetailsLabel.Clicked)
    async def action_show_details(self) -> None:
        await self.app.push_screen(WitnessDetailsScreen(witness_name=self.row_data.name))

    @property
    def action_identifier(self) -> str:
        return self.row_data.name

    def get_action_row_id(self) -> str:
        return WitnessesActions.create_action_row_id(self.action_identifier)

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


class WitnessManualSearch(Grid):
    LIMIT_MINIMUM: Final[int] = 1
    LIMIT_MAXIMUM: Final[int] = WitnessesDataRetrieval.TOP_WITNESSES_HARD_LIMIT

    @dataclass
    class Search(Message):
        """Emitted when the search button is pressed."""

        pattern: str
        limit: int

    class Clear(Message):
        """Emitted when the search input is cleared."""

    def __init__(self) -> None:
        super().__init__()

        self._witness_input = AccountNamePatternInput(
            "Witness name",
            always_show_title=True,
            required=False,
        )
        self._limit_input = IntegerInput(
            "Limit",
            MAX_NUMBER_OF_WITNESSES_IN_TABLE,
            validators=[
                Integer(
                    minimum=self.LIMIT_MINIMUM,
                    maximum=self.LIMIT_MAXIMUM,
                    failure_description=f"Must be between {self.LIMIT_MINIMUM} and {self.LIMIT_MAXIMUM}.",  # explicit description since textual Integer doesn't have description when NotANumber
                ),
            ],
            always_show_title=True,
            required=False,
        )

    def compose(self) -> ComposeResult:
        yield self._witness_input
        yield self._limit_input
        yield CliveButton("Search", variant="success", id_="witness-search-button")
        yield CliveButton("Clear", variant="error", id_="clear-custom-witnesses-button")

    @on(CliveButton.Pressed, "#witness-search-button")
    def search_witnesses(self) -> None:
        if not CliveValidatedInput.validate_many(self._witness_input, self._limit_input):
            return

        # already validated
        pattern = self._witness_input.value_or_error
        limit = self._limit_input.value_or_error

        self.post_message(self.Search(pattern, limit))

    @on(CliveButton.Pressed, "#clear-custom-witnesses-button")
    def clear_searched_witnesses(self) -> None:
        self._witness_input.input.clear()
        self._limit_input.input.value = str(self.LIMIT_MAXIMUM)
        self.post_message(self.Clear())


class WitnessActionRow(GovernanceActionRow):
    @staticmethod
    def create_action_row_id(identifier: str) -> str:
        return f"{convert_witness_name_to_widget_id(identifier)}-witness-action-row"


class WitnessesActions(GovernanceActions):
    NAME_OF_ACTION: ClassVar[str] = "Witness"

    async def mount_operations_from_cart(self) -> None:
        for operation in self.app.world.profile_data.cart:
            if isinstance(operation, AccountWitnessVoteOperation):
                await self.add_row(identifier=operation.witness, vote=operation.approve, pending=True)

    @staticmethod
    def create_action_row_id(identifier: str) -> str:
        return WitnessActionRow.create_action_row_id(identifier)

    def create_action_row(self, identifier: str, vote: bool, pending: bool) -> GovernanceActionRow:
        return WitnessActionRow(identifier, vote, pending)

    def hook_on_row_added(self) -> None:
        if self.actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify(f"The number of voted witnesses may not exceed {MAX_NUMBER_OF_WITNESSES_VOTES}")

    @property
    def actual_number_of_votes(self) -> int:
        amount = self.actions_votes
        if self.provider.is_content_set:
            amount += self.provider.content.number_of_votes
        return amount

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.screen.query_one(WitnessesDataProvider)


class WitnessesList(GovernanceListWidget[WitnessData]):
    def _create_row(self, data: WitnessData, *, even: bool = False) -> Witness:
        return Witness(data, even=even)


class WitnessesListHeader(GovernanceListHeader):
    def create_custom_columns(self) -> ComposeResult:
        yield Static("rank", id="rank-column")
        yield Static("witness", id="name-column")
        yield Static("votes", id="votes-column")

    def create_additional_headlines(self) -> ComposeResult:
        yield SectionTitle(
            f"Votes for witnesses cast by your proxy ({self.app.world.profile_data.working_account.data.proxy})"
            if self.is_proxy_set
            else "Modify the votes for witnesses"
        )


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
        return self.screen.query_one(WitnessesDataProvider)

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

        with ScrollablePart(), Horizontal(id="witnesses-content"):
            yield self.__witness_table
            yield WitnessesActions()
        yield WitnessManualSearch()

    def _create_operations(self) -> list[Operation] | None:
        actual_number_of_votes = self.screen.query_one(WitnessesActions).actual_number_of_votes

        if actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify(
                f"The number of voted witnesses may not exceed {MAX_NUMBER_OF_WITNESSES_VOTES}!", severity="error"
            )
            return None

        working_account_name = self.app.world.profile_data.working_account.name
        operations_to_perform = self.screen.query_one(WitnessesActions).actions_to_perform

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
