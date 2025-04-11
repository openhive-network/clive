from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Horizontal
from textual.events import Click
from textual.message import Message
from textual.validation import Integer
from textual.widgets import Label, Static

from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData, WitnessesDataRetrieval
from clive.__private.core.constants.node import MAX_NUMBER_OF_WITNESSES_VOTES
from clive.__private.models.schemas import AccountWitnessVoteOperation
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.data_providers.witnesses_data_provider import WitnessesDataProvider
from clive.__private.ui.dialogs import WitnessDetailsDialog
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActionRow,
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_tab_pane import (
    GovernanceTabPane,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceListHeader,
    GovernanceListWidget,
    GovernanceTable,
    GovernanceTableRow,
)
from clive.__private.ui.widgets.buttons import ClearButton, SearchButton
from clive.__private.ui.widgets.inputs.account_name_pattern_input import AccountNamePatternInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult
    from typing_extensions import TypeIs


MAX_NUMBER_OF_WITNESSES_IN_TABLE: Final[int] = 150


def convert_witness_name_to_widget_id(witness_name: str) -> str:
    return witness_name.replace(".", "")


class WitnessDetailsLabel(Label):
    class Clicked(Message):
        """Message send when DetailsLabel is clicked."""

    def __init__(self, witness_name: str, *, classes: str | None = None) -> None:
        super().__init__(renderable="details", classes=classes)
        self.tooltip = f"Click to see more details about {witness_name} witness."

    @on(Click)
    def clicked(self) -> None:
        self.post_message(self.Clicked())


class WitnessNameLabel(Label, CliveWidget):
    """Label with witness name."""

    def __init__(self, witness_name: str, classes: str) -> None:
        super().__init__(
            renderable=witness_name,
            id=f"{convert_witness_name_to_widget_id(witness_name)}-witness-info",
            classes=classes,
        )


class Witness(GovernanceTableRow[WitnessData]):
    """Check if there is a witness in the action table - if so, move True to the WitnessCheckbox parameter."""

    BINDINGS = [Binding("f3", "show_details", "Details")]

    @property
    def is_operation_in_cart(self) -> bool:
        expected_operation = AccountWitnessVoteOperation(
            account=self.profile.accounts.working.name,
            witness=self.row_data.name,
            approve=not self.row_data.voted,
        )
        return expected_operation in self.profile.transaction

    @property
    def action_identifier(self) -> str:
        return self.row_data.name

    def create_row_content(self) -> ComposeResult:
        class_name = f"witness-row-{self.evenness}"
        yield Label(
            str(self.row_data.rank) if self.row_data.rank is not None else f">{MAX_NUMBER_OF_WITNESSES_IN_TABLE}",
            classes=class_name,
        )
        yield WitnessNameLabel(
            self.row_data.name,
            classes=class_name,
        )
        yield Label(str(self.row_data.votes), classes=class_name)
        yield WitnessDetailsLabel(self.row_data.name, classes=class_name)

    @on(WitnessDetailsLabel.Clicked)
    async def action_show_details(self) -> None:
        await self.app.push_screen(WitnessDetailsDialog(witness_name=self.row_data.name))

    def get_action_row_id(self) -> str:
        return WitnessesActions.create_action_row_id(self.action_identifier)


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
                Integer(minimum=self.LIMIT_MINIMUM, maximum=self.LIMIT_MAXIMUM),
            ],
            always_show_title=True,
            required=False,
        )

    def compose(self) -> ComposeResult:
        yield self._witness_input
        yield self._limit_input
        yield SearchButton()
        yield ClearButton()

    @on(SearchButton.Pressed)
    def search_witnesses(self) -> None:
        if not CliveValidatedInput.validate_many(self._witness_input, self._limit_input):
            return

        # already validated
        pattern = self._witness_input.value_or_error
        limit = self._limit_input.value_or_error

        self.post_message(self.Search(pattern, limit))

    @on(ClearButton.Pressed)
    def clear_searched_witnesses(self) -> None:
        self._witness_input.input.clear()
        self._limit_input.input.value = str(self.LIMIT_MAXIMUM)
        self.post_message(self.Clear())


class WitnessActionRow(GovernanceActionRow):
    @staticmethod
    def create_action_row_id(identifier: str) -> str:
        return f"{convert_witness_name_to_widget_id(identifier)}-witness-action-row"


class WitnessesActions(GovernanceActions[AccountWitnessVoteOperation]):
    NAME_OF_ACTION: ClassVar[str] = "Witness"

    @property
    def actual_number_of_votes(self) -> int:
        amount = self.actions_votes
        if self.provider.is_content_set:
            amount += self.provider.content.number_of_votes
        return amount

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.screen.query_exactly_one(WitnessesDataProvider)

    @staticmethod
    def create_action_row_id(identifier: str) -> str:
        return WitnessActionRow.create_action_row_id(identifier)

    async def mount_operations_from_cart(self) -> None:
        for operation in self.profile.transaction:
            if self.should_be_added_to_actions(operation):
                await self.add_row(identifier=operation.witness, vote=operation.approve, hook_on_added=False)

    def should_be_added_to_actions(self, operation: object) -> TypeIs[AccountWitnessVoteOperation]:
        return (
            isinstance(operation, AccountWitnessVoteOperation)
            and operation.account == self.profile.accounts.working.name
        )

    def create_action_row(self, identifier: str, *, vote: bool) -> GovernanceActionRow:
        return WitnessActionRow(identifier, vote=vote)

    def hook_on_row_added(self) -> None:
        notification_message = f"The number of voted witnesses may not exceed {MAX_NUMBER_OF_WITNESSES_VOTES}"

        if self.app.is_notification_present(notification_message):
            return

        if self.actual_number_of_votes > MAX_NUMBER_OF_WITNESSES_VOTES:
            self.notify(notification_message, severity="warning")


class WitnessesList(GovernanceListWidget[WitnessData]):
    def _create_row(self, data: WitnessData, *, even: bool = False) -> Witness:
        return Witness(data, even=even)


class WitnessesListHeader(GovernanceListHeader):
    def create_custom_columns(self) -> ComposeResult:
        yield Static("Rank", classes="witnesses-table-header")
        yield Static("Witness", classes="witnesses-table-header witness-name-header")
        yield Static("Votes", classes="witnesses-table-header")

    def create_additional_headlines(self) -> ComposeResult:
        yield SectionTitle(
            f"Votes for witnesses cast by your proxy ({self.profile.accounts.working.data.proxy})"
            if self.is_proxy_set
            else "Modify the votes for witnesses"
        )


class WitnessesTable(GovernanceTable[WitnessData, WitnessesDataProvider]):
    MAX_ELEMENTS_ON_PAGE: ClassVar[int] = 30

    @property
    def provider(self) -> WitnessesDataProvider:
        return self.screen.query_exactly_one(WitnessesDataProvider)

    @property
    def data(self) -> list[WitnessData]:
        return list(self.provider.content.witnesses.values())

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


class Witnesses(GovernanceTabPane):
    """TabPane with all content about witnesses."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        super().__init__(title="Witnesses", id="witnesses")

    def compose(self) -> ComposeResult:
        self._witness_table = WitnessesTable()
        yield WitnessManualSearch()

        with ScrollablePart(), Horizontal(id="witnesses-content"):
            yield self._witness_table
            yield WitnessesActions()

    def add_operation_to_cart(self, identifier: str, *, vote: bool = False) -> None:
        operation = self._create_operation(identifier, vote=vote)

        if operation in self.profile.transaction:
            return

        self.profile.transaction.add_operation(operation)
        self.app.trigger_profile_watchers()

    def remove_operation_from_cart(self, identifier: str, *, vote: bool = False) -> None:
        self.profile.transaction.remove_operation(self._create_operation(identifier, vote=vote))
        self.app.trigger_profile_watchers()

    @on(WitnessManualSearch.Search)
    async def search_witnesses(self, message: WitnessManualSearch.Search) -> None:
        await self._witness_table.search_witnesses(pattern=message.pattern, limit=message.limit)

    @on(WitnessManualSearch.Clear)
    async def clear_searched_witnesses(self, _: WitnessManualSearch.Clear) -> None:
        await self._witness_table.clear_searched_witnesses()

    def _create_operation(self, witness: str, *, vote: bool) -> AccountWitnessVoteOperation:
        """Create account witness vote operation based on the given parameters."""
        return AccountWitnessVoteOperation(
            account=self.profile.accounts.working.name,
            witness=witness,
            approve=vote,
        )
