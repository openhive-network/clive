from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Click
from textual.widgets import Label, Static

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData
from clive.__private.ui.operations.governance_operations.governance_checkbox import GovernanceCheckbox
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

GovernanceDataTypes = TypeVar("GovernanceDataTypes", ProposalData, WitnessData)
GovernanceActionsIdentifiers = TypeVar("GovernanceActionsIdentifiers", int, str)


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class GovernanceListWidget(Vertical, CliveWidget, Generic[GovernanceDataTypes], AbstractClassMessagePump):
    """
    Governance data type is used to create elements of the list and must be passed generically.

    In this case, it must be either `ProposalsData` or `WitnessData`.
    """

    def __init__(self, elements: list[GovernanceDataTypes] | None) -> None:
        super().__init__()
        self.__elements_to_display: list[GovernanceDataTypes] | None = elements if elements is not None else None

    def compose(self) -> ComposeResult:
        if self.elements_to_display is None:
            self.loading = True
            return

        yield from self.show_elements()

    @abstractmethod
    def show_elements(self) -> ComposeResult:
        """Should yield witnesses or proposals widgets."""

    @property
    def elements_to_display(self) -> list[GovernanceDataTypes] | None:
        return self.__elements_to_display


class ArrowUpWidget(Static):
    def __init__(self, table_selector: str) -> None:
        super().__init__(renderable="↑ PgUp")
        self.__table_selector = table_selector

    @on(Click)
    async def previous_page(self) -> None:
        await self.app.query_one(self.__table_selector).previous_page()  # type: ignore[attr-defined]


class ArrowDownWidget(Static):
    def __init__(self, table_selector: str) -> None:
        super().__init__(renderable="↓ PgDn")
        self.__table_selector = table_selector

    @on(Click)
    async def next_page(self) -> None:
        await self.app.query_one(self.__table_selector).next_page()  # type: ignore[attr-defined]


class GovernanceListHeader(Grid, AbstractClassMessagePump):
    def __init__(self, table_selector: str):
        super().__init__()
        self.__table_selector = table_selector

        self.arrow_up = ArrowUpWidget(self.__table_selector)
        self.arrow_down = ArrowDownWidget(self.__table_selector)

        self.arrow_up.visible = False

    def compose(self) -> ComposeResult:
        yield self.arrow_up
        yield from self.create_custom_columns()
        yield self.arrow_down

    @abstractmethod
    def create_custom_columns(self) -> ComposeResult:
        """Should yield custom columns for each table."""


class GovernanceTableRow(Grid, CliveWidget, Generic[GovernanceDataTypes], AbstractClassMessagePump, can_focus=True):
    """
    Base class for rows in the tables in governance.

    The data type should be passed generically, in this case proposals or witness data.
    """

    BINDINGS = [
        Binding("pageup", "previous_page", "PgDn"),
        Binding("pagedown", "next_page", "PgUp"),
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    def __init__(self, row_data: GovernanceDataTypes, table_type: str, evenness: str = "even"):
        super().__init__()
        self.__row_data: GovernanceDataTypes = row_data
        self.__table_type = table_type
        self.__evenness = evenness

        self.governance_checkbox = GovernanceCheckbox(
            is_voted=row_data.voted,
            initial_state=self.is_operation_in_cart or self.is_already_in_actions_container,
            disabled=bool(self.app.world.profile_data.working_account.data.proxy) or self.is_operation_in_cart,
        )

    def on_mount(self) -> None:
        self.watch(self.governance_checkbox, "disabled", callback=self.dimm_on_disabled_checkbox)

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

    async def action_next_page(self) -> None:
        await self.app.query_one(self.__table_type).next_page()  # type: ignore[attr-defined]

    async def action_previous_page(self) -> None:
        await self.app.query_one(self.__table_type).previous_page()  # type: ignore[attr-defined]

    def action_toggle_checkbox(self) -> None:
        self.governance_checkbox.toggle()

    @on(GovernanceCheckbox.Changed)
    async def modify_action_status(self) -> None:
        await self.move_row_to_actions()

    @abstractmethod
    async def move_row_to_actions(self) -> None:
        """Should query and update item actions."""

    @abstractmethod
    def create_row_content(self) -> ComposeResult:
        """Should contain all the information that should be displayed about the item."""

    @property
    @abstractmethod
    def is_already_in_actions_container(self) -> bool:
        """Should check if operation is already in the actions container."""

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


class GovernanceActionRow(Horizontal, Generic[GovernanceActionsIdentifiers], AbstractClassMessagePump):
    """
    The `action_identifier` is used to pass the ID of the proposal or the name of the witness.

    The type of the identifier must be passed generically as either `str` or `int`.
    """

    def __init__(self, identifier: GovernanceActionsIdentifiers, vote: bool, pending: bool = False):
        self.__identifier: GovernanceActionsIdentifiers = identifier

        super().__init__(id=self.create_widget_id())
        self.__vote = vote
        self.__pending = pending

    def compose(self) -> ComposeResult:
        if self.__pending:
            yield Label("Pending", classes="action-pending action-label")
            yield Label(self.action_identifier, classes="action-identifier")
            return

        if self.__vote:
            yield Label("Vote", classes="action-vote action-label")
        else:
            yield Label("Unvote", classes="action-unvote action-label")
        yield Label(self.action_identifier, classes="action-identifier")

    @property
    def action_identifier(self) -> str:
        return str(self.__identifier)

    @abstractmethod
    def create_widget_id(self) -> str:
        pass


class GovernanceActions(VerticalScroll, CanFocusWithScrollbarsOnly):
    """
    Contains a table of operations to be performed after confirmation.

    Attributes
    ----------
    __actions_to_perform (dict): a dict with proposal_id or witness name as key and action to pe performed as value
    """

    def __init__(self) -> None:
        self.__actions_to_perform: dict[str, bool] = {}
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static("Actions to be performed:", id="actions-header")
        with Horizontal(id="name-and-action"):
            yield Static("Action", id="action-row")
            yield from self.name_action_type()

    async def on_mount(self) -> None:  # type: ignore[override]
        await self.mount_operations_from_cart()

    def add_to_actions(self, identifier: str, vote: bool) -> None:
        self.__actions_to_perform[identifier] = vote

    def delete_from_actions(self, identifier: str) -> None:
        self.__actions_to_perform.pop(identifier)

    @property
    def actions_to_perform(self) -> dict[str, bool]:
        return self.__actions_to_perform

    @staticmethod
    @abstractmethod
    def get_action_id(identifier: str) -> str:
        """Should return id of the action row."""

    @abstractmethod
    async def mount_operations_from_cart(self) -> None:
        """Should check cart and mount all appropriate operations."""

    @abstractmethod
    def name_action_type(self) -> ComposeResult:
        """Should yield actually `Witness` or `Proposal`."""


class GovernanceTable(Vertical, CliveWidget, AbstractClassMessagePump, can_focus=False):
    def __init__(self) -> None:
        super().__init__()
        self.__element_index = 0

        self.__header = self.create_header()
        self.__is_loading = True

    async def loading_set(self) -> None:
        self.__is_loading = True
        with contextlib.suppress(NoMatches):
            selected_list = self.query_one(self.define_list_type())
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

    async def next_page(self) -> None:
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

    async def previous_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user going to a page with a negative index by key binding
        if self.__element_index <= 0:
            self.notify("No witnesses on the previous page", severity="warning")
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

    @abstractmethod
    def define_list_type(self) -> type[GovernanceListWidget[GovernanceDataTypes]]:
        """Should return type of witnesses or proposals list."""

    @abstractmethod
    def create_header(self) -> GovernanceListHeader:
        pass

    @abstractmethod
    async def sync_list(self, focus_first_element: bool = False) -> None:
        pass

    @property
    @abstractmethod
    def max_elements_on_page(self) -> int:
        pass

    @property
    @abstractmethod
    def amount_of_fetched_elements(self) -> int:
        pass
