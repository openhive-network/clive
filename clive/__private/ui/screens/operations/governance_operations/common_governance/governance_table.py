from __future__ import annotations

import contextlib
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from textual import on
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Label

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.commands.data_retrieval.proposals_data import Proposal as ProposalData
from clive.__private.core.commands.data_retrieval.witnesses_data import WitnessData
from clive.__private.core.constants.tui.texts import LOADING_TEXT
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.data_providers.abc.data_provider import DataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.governance_operations.governance_checkbox import GovernanceCheckbox
from clive.__private.ui.widgets.buttons import PageDownOneLineButton, PageUpOneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult

GovernanceDataT = TypeVar("GovernanceDataT", ProposalData, WitnessData)
GovernanceDataProviderT = TypeVar("GovernanceDataProviderT", bound=DataProvider[Any])


class GovernanceListHeader(Grid, CliveWidget, AbstractClassMessagePump):
    """Widget representing the header of a list that allows page switching using PgUp and PgDn."""

    def __init__(self) -> None:
        super().__init__()

        self.button_up = PageUpOneLineButton()
        self.button_down = PageDownOneLineButton()

        self.button_up.visible = False

    @abstractmethod
    def create_custom_columns(self) -> ComposeResult:
        """
        Yield custom columns for each table.

        Returns:
            Custom columns to be displayed in the header.
        """

    @property
    def is_proxy_set(self) -> bool:
        return bool(self.profile.accounts.working.data.proxy)

    def compose(self) -> ComposeResult:
        yield from self.create_additional_headlines()
        yield self.button_up
        yield from self.create_custom_columns()
        yield self.button_down

    def create_additional_headlines(self) -> ComposeResult:
        """Yield custom headlines that will be placed above the arrows and column names."""
        return []


class GovernanceListWidget(Vertical, CliveWidget, Generic[GovernanceDataT], AbstractClassMessagePump):  # noqa: UP046
    """
    A widget containing a list of `GovernanceTableRow` widgets.

    Args:
        data: A collection of data used to fill the rows.
    """

    def __init__(self, data: list[GovernanceDataT] | None) -> None:
        super().__init__()
        self._data: list[GovernanceDataT] | None = data

    @abstractmethod
    def _create_row(self, data: GovernanceDataT, *, even: bool = False) -> GovernanceTableRow[GovernanceDataT]:
        """Return row widget."""

    @property
    def is_data_empty(self) -> bool:
        if self._data is None:
            #  When _data is None - still waiting for the response.
            return False

        return not bool(self._data)

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


class GovernanceTableRow(Grid, CliveWidget, Generic[GovernanceDataT], AbstractClassMessagePump, can_focus=True):  # noqa: UP046
    """
    Base class for rows in governance tables. The type of data used to create rows must be passed generically.

    Widgets that belong to the row are displayed by `create_row_content` and are defined by the inheriting class.

    Args:
        row_data: Data used to create the row of the table.
        even: Whether the row is even or odd.

    Attributes:
        BINDINGS: Key bindings for the row.
    """

    BINDINGS = [
        Binding("enter", "toggle_checkbox", "", show=False),
    ]

    @dataclass
    class ChangeActionStatus(Message):
        """Message send when user request by GovernanceCheckbox to change the action status.

        Attributes:
            action_identifier: Identifier of the action to be performed, e.g. witness name or proposal id.
            vote: Action to be performed - vote or not.
            add: Indicates if the action should be added to the actions container or removed.
        """

        action_identifier: str
        vote: bool
        add: bool

    def __init__(self, row_data: GovernanceDataT, *, even: bool = False) -> None:
        super().__init__()
        self._row_data: GovernanceDataT = row_data
        self._evenness = "even" if even else "odd"

    @property
    @abstractmethod
    def action_identifier(self) -> str:
        """Return witness name or proposal id to mount the action correctly."""

    @property
    @abstractmethod
    def is_operation_in_cart(self) -> bool:
        """Check if operation is already in the cart."""

    @abstractmethod
    def create_row_content(self) -> ComposeResult:
        """Contains all the information that should be displayed about the item."""

    @abstractmethod
    def get_action_row_id(self) -> str:
        """Return an id of the action row."""

    @on(GovernanceCheckbox.Clicked)
    def focus_myself(self) -> None:
        self.focus()

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
        return self._row_data

    @property
    def evenness(self) -> str:
        return self._evenness

    def on_mount(self) -> None:
        self.watch(self.governance_checkbox, "disabled", callback=self.dimm_on_disabled_checkbox)

    def compose(self) -> ComposeResult:
        self.governance_checkbox = GovernanceCheckbox(
            is_voted=self._row_data.voted,
            initial_state=self.is_operation_in_cart,
            disabled=bool(self.profile.accounts.working.data.proxy),
        )
        yield self.governance_checkbox
        yield from self.create_row_content()

    def dimm_on_disabled_checkbox(self, value: bool) -> None:  # noqa: FBT001
        if value:
            self.add_class("dimmed")
            return
        self.remove_class("dimmed")

    def action_toggle_checkbox(self) -> None:
        self.governance_checkbox.toggle()


class GovernanceTable(
    Vertical,
    CliveWidget,
    Generic[GovernanceDataT, GovernanceDataProviderT],  # noqa: UP046
    AbstractClassMessagePump,
    can_focus=False,
):
    MAX_ELEMENTS_ON_PAGE: ClassVar[int] = 10

    DEFAULT_CSS = get_css_from_relative_path(__file__)
    BINDINGS = [
        Binding("pageup", "previous_page", "PgDn"),
        Binding("pagedown", "next_page", "PgUp"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._element_index = 0

        self._header = self.create_header()
        self._is_loading = True

    @property
    @abstractmethod
    def data(self) -> list[GovernanceDataT]:
        """Return data from data provider."""

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

    @property
    def is_data_available(self) -> bool:
        return self.provider.is_content_set

    @property
    def data_chunk(self) -> list[GovernanceDataT] | None:
        if not self.is_data_available:
            return None

        return self.data[self._element_index : self._element_index + self.MAX_ELEMENTS_ON_PAGE]

    @property
    def data_length(self) -> int:
        if not self.is_data_available:
            return 0

        return len(self.data)

    @property
    def element_index(self) -> int:
        return self._element_index

    @property
    def header(self) -> GovernanceListHeader:
        return self._header

    @property
    def is_proxy_set(self) -> bool:
        return bool(self.profile.accounts.working.data.proxy)

    @on(PageDownOneLineButton.Pressed)
    async def action_next_page(self) -> None:
        if self._is_loading:
            return

        # It is used to prevent the user from switching to an empty page by key binding
        if self.data_length - self.MAX_ELEMENTS_ON_PAGE <= self._element_index:
            self.notify("No elements on the next page", severity="warning")
            return

        self._element_index += self.MAX_ELEMENTS_ON_PAGE

        self._header.button_up.visible = True

        if self.data_length - self.MAX_ELEMENTS_ON_PAGE <= self._element_index:
            self._header.button_down.visible = False

        await self.sync_list(focus_first_element=True)

    @on(PageUpOneLineButton.Pressed)
    async def action_previous_page(self) -> None:
        if self._is_loading:
            return

        # It is used to prevent the user going to a page with a negative index by key binding
        if self._element_index <= 0:
            self.notify("No elements on the previous page", severity="warning")
            return

        self._header.button_down.visible = True

        self._element_index -= self.MAX_ELEMENTS_ON_PAGE

        if self._element_index <= 0:
            self._header.button_up.visible = False

        await self.sync_list(focus_first_element=True)

    def compose(self) -> ComposeResult:
        yield self.header

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", callback=lambda: self.sync_list())

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
        self._is_loading = True
        with contextlib.suppress(NoMatches):
            selected_list = self.query_exactly_one(GovernanceListWidget)  # type: ignore[type-abstract]
            await selected_list.query("*").remove()
            await selected_list.mount(Label(LOADING_TEXT.capitalize()))

    def set_loaded(self) -> None:
        self._is_loading = False

    async def reset_page(self) -> None:
        self._element_index = 0
        self._header.button_up.visible = False
        self._header.button_down.visible = True

        if not self._is_loading:
            await self.sync_list()
