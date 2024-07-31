from __future__ import annotations

import contextlib
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.css.query import NoMatches
from textual.events import Click
from textual.message import Message
from textual.widgets import Label, Static

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData
from clive.__private.ui.data_providers.abc.data_provider import DataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.governance_operations.governance_checkbox import GovernanceCheckbox
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

GovernanceDataT = TypeVar("GovernanceDataT", ProposalData, WitnessData)
GovernanceDataProviderT = TypeVar("GovernanceDataProviderT", bound=DataProvider[Any])


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


class GovernanceListHeader(Grid, CliveWidget, AbstractClassMessagePump):
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
        """Yield custom columns for each table."""

    def create_additional_headlines(self) -> ComposeResult:
        """Yield custom headlines that will be placed above the arrows and column names."""
        return []

    @property
    def is_proxy_set(self) -> bool:
        return bool(self.profile_data.accounts.working.data.proxy)


class GovernanceListWidget(Vertical, CliveWidget, Generic[GovernanceDataT], AbstractClassMessagePump):
    """A widget containing a list of `GovernanceTableRow` widgets."""

    def __init__(self, data: list[GovernanceDataT] | None) -> None:
        """
        Initialize the GovernanceListWidget.

        Args:
        ----
        data: list of data to fill in the `GovernanceTableRow` widgets.
        """
        super().__init__()
        self._data: list[GovernanceDataT] | None = data

    @abstractmethod
    def _create_row(self, data: GovernanceDataT, *, even: bool = False) -> GovernanceTableRow[GovernanceDataT]:
        """Return row widget."""

    def compose(self) -> ComposeResult:
        if self.is_data_empty:
            yield Label("No elements to display")
            return
        yield from self._create_rows()

    def _create_rows(self) -> ComposeResult:
        if self._data is not None:
            for idx, element in enumerate(self._data):
                if idx % 2 == 0:
                    yield self._create_row(element, even=True)
                else:
                    yield self._create_row(element)

    @property
    def is_data_empty(self) -> bool:
        if self._data is None:
            #  When _data is None - still waiting for the response.
            return False

        if len(self._data) == 0:
            return True

        return False


class GovernanceTableRow(Grid, CliveWidget, Generic[GovernanceDataT], AbstractClassMessagePump, can_focus=True):
    """
    Base class for rows in governance tables. The type of data used to create rows must be passed generically.

    Widgets that belong to the row are displayed by `create_row_content` and are defined by the inheriting class.
    """

    BINDINGS = [
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    @dataclass
    class ChangeActionStatus(Message):
        """Message send when user request by GovernanceCheckbox to change the action status."""

        action_identifier: str
        vote: bool
        add: bool
        """If True, add action to the actions container, if False - remove."""

    def __init__(self, row_data: GovernanceDataT, *, even: bool = False) -> None:
        """
        Initialize the GovernanceTableRow.

        Args:
        ----
        row_data: Data used to create the row of the table.
        even: Whether the row is even or odd.
        """
        super().__init__()
        self.__row_data: GovernanceDataT = row_data
        self.__evenness = "even" if even else "odd"

    def on_mount(self) -> None:
        self.watch(self.governance_checkbox, "disabled", callback=self.dimm_on_disabled_checkbox)

    def compose(self) -> ComposeResult:
        self.governance_checkbox = GovernanceCheckbox(
            is_voted=self.__row_data.voted,
            initial_state=self.is_operation_in_cart or self.is_already_in_actions_container,
            disabled=bool(self.profile_data.accounts.working.data.proxy) or self.is_operation_in_cart,
        )
        yield self.governance_checkbox
        yield from self.create_row_content()

    @on(GovernanceCheckbox.Clicked)
    def focus_myself(self) -> None:
        self.focus()

    def dimm_on_disabled_checkbox(self, value: bool) -> None:  # noqa: FBT001
        if value:
            self.add_class("dimmed")
            return
        self.remove_class("dimmed")

    def action_toggle_checkbox(self) -> None:
        self.governance_checkbox.toggle()

    @on(GovernanceCheckbox.Changed)
    async def change_action_status(self) -> None:
        self.post_message(
            self.ChangeActionStatus(
                action_identifier=self.action_identifier,
                vote=not self.row_data.voted,
                add=self.governance_checkbox.value,
            )
        )

    @property
    def row_data(self) -> GovernanceDataT:
        return self.__row_data

    @property
    def evenness(self) -> str:
        return self.__evenness

    @abstractmethod
    def create_row_content(self) -> ComposeResult:
        """Contains all the information that should be displayed about the item."""

    @property
    @abstractmethod
    def action_identifier(self) -> str:
        """Return witness name or proposal id to mount the action correctly."""

    @property
    def is_already_in_actions_container(self) -> bool:
        """Check if operation is already in the action container."""
        try:
            self.screen.get_widget_by_id(self.get_action_row_id())
        except NoMatches:
            return False
        else:
            return True

    @abstractmethod
    def get_action_row_id(self) -> str:
        """Return an id of the action row."""

    @property
    @abstractmethod
    def is_operation_in_cart(self) -> bool:
        """Check if operation is already in the cart."""


class GovernanceTable(
    Vertical, CliveWidget, Generic[GovernanceDataT, GovernanceDataProviderT], AbstractClassMessagePump, can_focus=False
):
    MAX_ELEMENTS_ON_PAGE: ClassVar[int] = 10

    DEFAULT_CSS = get_css_from_relative_path(__file__)
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

    def on_mount(self) -> None:
        def delegate_work() -> None:
            self.run_worker(self.sync_list())

        self.watch(self.provider, "_content", callback=delegate_work)

    async def sync_list(self, *, focus_first_element: bool = False) -> None:
        await self.loading_set()

        new_list = self.create_new_list_widget()

        with self.app.batch_update():
            await self.query(GovernanceListWidget).remove()  # type: ignore[type-abstract]
            await self.mount(new_list)

        if focus_first_element:
            first_row = self.query(GovernanceTableRow).first()  # type: ignore[type-abstract]
            first_row.focus()

        self.set_loaded()

    async def loading_set(self) -> None:
        self.__is_loading = True
        with contextlib.suppress(NoMatches):
            selected_list = self.query_one(GovernanceListWidget)  # type: ignore[type-abstract]
            await selected_list.query("*").remove()
            await selected_list.mount(Label("Loading..."))

    def set_loaded(self) -> None:
        self.__is_loading = False

    @on(ArrowDownWidget.Clicked)
    async def action_next_page(self) -> None:
        if self.__is_loading:
            return

        # It is used to prevent the user from switching to an empty page by key binding
        if self.data_length - self.MAX_ELEMENTS_ON_PAGE <= self.__element_index:
            self.notify("No elements on the next page", severity="warning")
            return

        self.__element_index += self.MAX_ELEMENTS_ON_PAGE

        self.__header.arrow_up.visible = True

        if self.data_length - self.MAX_ELEMENTS_ON_PAGE <= self.__element_index:
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

        self.__element_index -= self.MAX_ELEMENTS_ON_PAGE

        if self.__element_index <= 0:
            self.__header.arrow_up.visible = False

        await self.sync_list(focus_first_element=True)

    async def reset_page(self) -> None:
        self.__element_index = 0
        self.__header.arrow_up.visible = False
        self.__header.arrow_down.visible = True

        if not self.__is_loading:
            await self.sync_list()

    @property
    @abstractmethod
    def data(self) -> list[GovernanceDataT]:
        """Return data from data provider."""

    @property
    def is_data_available(self) -> bool:
        return self.provider.is_content_set

    @property
    def data_chunk(self) -> list[GovernanceDataT] | None:
        if not self.is_data_available:
            return None

        return self.data[self.__element_index : self.__element_index + self.MAX_ELEMENTS_ON_PAGE]

    @property
    def data_length(self) -> int:
        if not self.is_data_available:
            return 0

        return len(self.data)

    @property
    def element_index(self) -> int:
        return self.__element_index

    @property
    def header(self) -> GovernanceListHeader:
        return self.__header

    @property
    def is_proxy_set(self) -> bool:
        return bool(self.profile_data.accounts.working.data.proxy)

    @property
    @abstractmethod
    def provider(self) -> GovernanceDataProviderT:
        """Query and return appropriate data provider."""

    @abstractmethod
    def create_new_list_widget(self) -> GovernanceListWidget[GovernanceDataT]:
        """Return the instance of the new witnesses or proposals list."""

    @abstractmethod
    def create_header(self) -> GovernanceListHeader:
        pass
