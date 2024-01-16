from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Click
from textual.message import Message
from textual.widgets import Label, Static

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData
from clive.__private.ui.operations.governance_operations.governance_checkbox import GovernanceCheckbox
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.data_providers.abc.data_provider import DataProvider, ProviderContentT

GovernanceDataTypes = TypeVar("GovernanceDataTypes", ProposalData, WitnessData)
GovernanceActionsIdentifiersT = TypeVar("GovernanceActionsIdentifiersT", int, str)


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class GovernanceListWidget(Vertical, CliveWidget, Generic[GovernanceDataTypes], AbstractClassMessagePump):
    """
    Governance data is used to create elements of the list, and its type must be passed generically.

    Args:
    ----
    elements (list[GovernanceDataTypes] | None): List of elements to be displayed in the table. Precise type must be passed generically!
    """

    def __init__(self, elements: list[GovernanceDataTypes] | None) -> None:
        super().__init__()
        self.__elements_to_display: list[GovernanceDataTypes] | None = elements

    def compose(self) -> ComposeResult:
        yield from self.show_elements()

    @abstractmethod
    def show_elements(self) -> ComposeResult:
        """Should yield witnesses or proposals widgets."""

    @property
    def elements_to_display(self) -> list[GovernanceDataTypes] | None:
        return self.__elements_to_display


class ArrowUpWidget(Static):
    class Clicked(Message):
        """Message send when WitnessCheckbox is clicked."""

    def __init__(self) -> None:
        super().__init__(renderable="↑ PgUp")

    @on(Click)
    async def clicked(self) -> None:
        self.post_message(self.Clicked())


class ArrowDownWidget(Static):
    class Clicked(Message):
        """Message send when WitnessCheckbox is clicked."""

    def __init__(self) -> None:
        super().__init__(renderable="↓ PgDn")

    @on(Click)
    async def clicked(self) -> None:
        self.post_message(self.Clicked())


class GovernanceListHeader(Grid, AbstractClassMessagePump):
    """Widget representing the header of a list that allows page switching using PgUp and PgDn."""

    def __init__(self) -> None:
        super().__init__()

        self.arrow_up = ArrowUpWidget()
        self.arrow_down = ArrowDownWidget()

        self.arrow_up.visible = False

    def compose(self) -> ComposeResult:
        yield from self.create_additional_headlines()
        yield self.arrow_up
        yield from self.create_custom_columns()
        yield self.arrow_down

    @abstractmethod
    def create_custom_columns(self) -> ComposeResult:
        """Should yield custom columns for each table."""

    @abstractmethod
    def create_additional_headlines(self) -> ComposeResult:
        """
        Should yield custom headlines that will be placed above the arrows and column names.

        If no custom headlines should yield an empty element (placeholder).
        """


class GovernanceTableRow(Grid, CliveWidget, Generic[GovernanceDataTypes], AbstractClassMessagePump, can_focus=True):
    """
    Base class for rows in governance tables. The type of data used to create rows must be passed generically.

    Args:
    ----
    row_data (GovernanceDataTypes): Data used to create the row of the table, either `ProposalsData` or `WitnessesData` in this case.
    table_selector (GovernanceTable): Type of the table class to which the row belongs.
    evenness (str): Defaults to "even."

    Widgets that belong to the row are displayed by `create_row_content` and are defined by the inheriting class.
    """

    BINDINGS = [
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    def __init__(self, row_data: GovernanceDataTypes, evenness: str = "even"):
        super().__init__()
        self.__row_data: GovernanceDataTypes = row_data
        self.__evenness = evenness

        self.governance_checkbox = GovernanceCheckbox(
            is_voted=row_data.voted,
            initial_state=self.is_operation_in_cart or self.is_already_in_actions_container,
            disabled=bool(self.app.world.profile_data.working_account.data.proxy) or self.is_operation_in_cart,
        )

    def on_mount(self) -> None:
        self.watch(self.governance_checkbox, "disabled", callback=self.dimm_on_disabled_checkbox)

    async def move_row_to_actions(self) -> None:
        actions_table = self.app.query_one(self.actions_type)  # type: ignore[arg-type]
        if self.governance_checkbox.value:
            await actions_table.mount_action(identifier=self.action_identifier, vote=not self.row_data.voted)  # type: ignore[arg-type]
            return
        await actions_table.unmount_action(identifier=self.action_identifier, vote=not self.row_data.voted)  # type: ignore[arg-type]

    def compose(self) -> ComposeResult:
        yield self.governance_checkbox
        yield from self.create_row_content()

    @on(GovernanceCheckbox.Clicked)
    def focus_myself(self) -> None:
        self.focus()

    def dimm_on_disabled_checkbox(self, value: bool) -> None:
        if value:
            self.add_class("dimmed")
            return
        self.remove_class("dimmed")

    def action_toggle_checkbox(self) -> None:
        self.governance_checkbox.toggle()

    @on(GovernanceCheckbox.Changed)
    async def modify_action_status(self) -> None:
        await self.move_row_to_actions()

    @abstractmethod
    def create_row_content(self) -> ComposeResult:
        """Should contain all the information that should be displayed about the item."""

    @property
    @abstractmethod
    def actions_type(self) -> type[GovernanceActions[GovernanceActionsIdentifiersT]]:
        """Should return type of actions table that action will be mounted."""

    @property
    @abstractmethod
    def action_identifier(self) -> GovernanceActionsIdentifiersT:
        """Should return witness name or proposal id to mount the action correctly."""

    @property
    @abstractmethod
    def is_already_in_actions_container(self) -> bool:
        """Should check if operation is already in the action container."""

    @property
    @abstractmethod
    def is_operation_in_cart(self) -> bool:
        """Should check if operation is already in the cart."""

    @property
    def row_data(self) -> GovernanceDataTypes:
        return self.__row_data

    @property
    def evenness(self) -> str:
        return self.__evenness


class GovernanceActionRow(Horizontal, Generic[GovernanceActionsIdentifiersT], AbstractClassMessagePump):
    """
    Class that displays either the name of the witness or the ID of the proposal - chosen generically based on the action to be performed.

    Args:
    ----
    action_identifier (GovernanceActionsIdentifiers): Used to pass the ID of the proposal or the name of the witness. Type chosen generically - int or str.
    vote (bool): Action to be performed - vote or not.
    pending (bool): Indicates if the operation with such identifier is already in the cart. Default is False.
    """

    def __init__(self, identifier: GovernanceActionsIdentifiersT, vote: bool, pending: bool = False):
        self.__identifier: GovernanceActionsIdentifiersT = identifier

        super().__init__(id=self.create_widget_id())
        self.__vote = vote
        self.__pending = pending

    def compose(self) -> ComposeResult:
        if self.__pending:
            yield Label("Pending", classes="action-pending action-label")
            yield Label(str(self.action_identifier), classes="action-identifier")
            return

        if self.__vote:
            yield Label("Vote", classes="action-vote action-label")
        else:
            yield Label("Unvote", classes="action-unvote action-label")
        yield Label(str(self.action_identifier), classes="action-identifier")

    @property
    def action_identifier(self) -> GovernanceActionsIdentifiersT:
        return self.__identifier

    @abstractmethod
    def create_widget_id(self) -> str:
        pass


class GovernanceActions(VerticalScroll, Generic[GovernanceActionsIdentifiersT], CanFocusWithScrollbarsOnly):
    """
    Contains a table of actions to be performed after confirmation. Type of the action identifier (witness name or proposal id) must be specified generically.

    Attributes
    ----------
    __actions_to_perform (dict): a dict with proposal_id or witness name as key and action to pe performed as value
    """

    def __init__(self) -> None:
        self.__actions_to_perform: dict[GovernanceActionsIdentifiersT, bool] = {}
        super().__init__()
        self.__actions_votes = 0

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-row")
            yield Static(self.name_of_action, id="action-name-row")

    async def on_mount(self) -> None:  # type: ignore[override]
        await self.mount_operations_from_cart()

    async def mount_action(
        self, identifier: GovernanceActionsIdentifiersT, vote: bool = False, pending: bool = False
    ) -> None:
        # check if action is already in the list, if so - return

        with contextlib.suppress(NoMatches):
            self.query_one(self.get_action_id(identifier))
            return

        await self.mount(self.create_action_row(identifier, vote, pending))

        if vote:
            self.__actions_votes += 1
        else:
            self.__actions_votes -= 1

        self.create_number_of_votes_restriction()

        if not pending:
            self.add_to_actions(identifier, vote)

    async def unmount_action(self, identifier: GovernanceActionsIdentifiersT, vote: bool = False) -> None:
        try:
            await self.query_one(self.get_action_id(identifier)).remove()
        except NoMatches:
            return

        if vote:
            self.__actions_votes -= 1
        else:
            self.__actions_votes += 1

        self.delete_from_actions(identifier)

    def add_to_actions(self, identifier: GovernanceActionsIdentifiersT, vote: bool) -> None:
        self.__actions_to_perform[identifier] = vote

    def delete_from_actions(self, identifier: GovernanceActionsIdentifiersT) -> None:
        self.__actions_to_perform.pop(identifier)

    @property
    def actions_votes(self) -> int:
        return self.__actions_votes

    @property
    def actions_to_perform(self) -> dict[GovernanceActionsIdentifiersT, bool]:
        return self.__actions_to_perform

    @staticmethod
    @abstractmethod
    def get_action_id(identifier: GovernanceActionsIdentifiersT) -> str:
        """Should return id of the action row."""

    @abstractmethod
    async def mount_operations_from_cart(self) -> None:
        """Should check cart and mount all appropriate operations."""

    @abstractmethod
    def create_action_row(
        self, identifier: GovernanceActionsIdentifiersT, vote: bool, pending: bool
    ) -> GovernanceActionRow[GovernanceActionsIdentifiersT]:
        pass

    @abstractmethod
    def create_number_of_votes_restriction(self) -> None:
        """It should only be filled in if there is a limit on the number of votes - if not, a `pass` should be implemented."""

    @property
    @abstractmethod
    def name_of_action(self) -> str:
        """Should return `Proposal` or `Witness`."""


class GovernanceTable(Vertical, CliveWidget, AbstractClassMessagePump, can_focus=False):
    BINDINGS = [
        Binding("pageup", "previous_page", "PgDn"),
        Binding("pagedown", "next_page", "PgUp"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__element_index = 0

        self.__header = self.create_header()
        self.__is_loading = True

    def compose(self) -> ComposeResult:
        yield self.header

    async def sync_list(self, focus_first_element: bool = False) -> None:
        await self.loading_set()

        new_list = self.create_new_list_widget()

        with self.app.batch_update():
            await self.query(GovernanceListWidget).remove()  # type: ignore[type-abstract]
            await self.mount(new_list)

        if focus_first_element:
            first_row = self.query(GovernanceTableRow).first()  # type: ignore[type-abstract]
            first_row.focus()

        self.set_loaded()

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", callback=lambda: self.sync_list())

    async def loading_set(self) -> None:
        self.__is_loading = True
        with contextlib.suppress(NoMatches):
            selected_list = self.query_one(GovernanceListWidget)  # type: ignore[type-abstract]
            await selected_list.query("*").remove()
            await selected_list.mount(Label("Loading..."))

    async def reset_page(self) -> None:
        self.__element_index = 0
        self.__header.arrow_up.visible = False
        self.__header.arrow_down.visible = True

        if not self.__is_loading:
            await self.sync_list()

    def set_loaded(self) -> None:
        self.__is_loading = False

    @on(ArrowDownWidget.Clicked)
    async def action_next_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user from switching to an empty page by key binding
        if self.amount_of_fetched_elements - self.max_elements_on_page <= self.__element_index + 1:
            self.notify("No elements on the next page", severity="warning")
            return

        self.__element_index += self.max_elements_on_page

        self.__header.arrow_up.visible = True

        if self.amount_of_fetched_elements - self.max_elements_on_page <= self.__element_index:
            self.__header.arrow_down.visible = False

        await self.sync_list(focus_first_element=True)

    @on(ArrowUpWidget.Clicked)
    async def action_previous_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user going to a page with a negative index by key binding
        if self.__element_index <= 0:
            self.notify("No elements on the previous page", severity="warning")
            return

        self.__header.arrow_down.visible = True

        self.__element_index -= self.max_elements_on_page

        if self.__element_index <= 0:
            self.__header.arrow_up.visible = False

        await self.sync_list(focus_first_element=True)

    @property
    def element_index(self) -> int:
        return self.__element_index

    @property
    def header(self) -> GovernanceListHeader:
        return self.__header

    @property
    @abstractmethod
    def provider(self) -> DataProvider[ProviderContentT]:
        """Should query and return appropriate data provider."""

    @abstractmethod
    def create_new_list_widget(self) -> GovernanceListWidget[GovernanceDataTypes]:
        """Should return the instance of the new witnesses or proposals list."""

    @abstractmethod
    def create_header(self) -> GovernanceListHeader:
        pass

    @property
    @abstractmethod
    def max_elements_on_page(self) -> int:
        pass

    @property
    @abstractmethod
    def amount_of_fetched_elements(self) -> int:
        pass
