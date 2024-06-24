from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_operation_details, humanize_operation_name
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class ButtonMoveUp(CliveButton):
    """Button used for moving the operation up in the cart."""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↑", id_="move-up-button", disabled=disabled)


class ButtonMoveDown(CliveButton):
    """Button used for moving the operation down in the cart."""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↓", id_="move-down-button", disabled=disabled)


class ButtonDelete(CliveButton):
    """Button used for removing the operation from cart."""

    def __init__(self) -> None:
        super().__init__("Remove", id_="delete-button", variant="error")


class CartItem(CliveCheckerboardTableRow, CliveWidget, can_focus=True):
    """Row of CartTable."""

    BINDINGS = [
        Binding("ctrl+up", "select_previous", "Prev"),
        Binding("ctrl+down", "select_next", "Next"),
    ]

    class Delete(Message):
        def __init__(self, widget: CartItem) -> None:
            self.widget = widget
            super().__init__()

    class Move(Message):
        def __init__(self, from_idx: int, to_idx: int) -> None:
            self.from_idx = from_idx
            self.to_idx = to_idx
            super().__init__()

    class Focus(Message):
        """Message sent when other CartItem should be focused."""

        def __init__(self, target_idx: int) -> None:
            self.target_idx = target_idx
            super().__init__()

    def __init__(self, operation_idx: int) -> None:
        self.__idx = operation_idx
        assert self.is_valid(), "During construction, index has to be valid"
        super().__init__(
            CliveCheckerBoardTableCell(self.get_operation_index(), classes="index"),
            CliveCheckerBoardTableCell(self.get_operation_name(), classes="operation-type"),
            CliveCheckerBoardTableCell(self.get_operation_details(), classes="operation-details"),
            CliveCheckerBoardTableCell(
                Horizontal(
                    ButtonMoveUp(disabled=self.__is_first), ButtonMoveDown(disabled=self.__is_last), ButtonDelete()
                ),
                classes="actions",
            ),
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(idx={self.__idx})"

    def on_mount(self) -> None:
        if self.__is_first:
            self.unbind("ctrl+up")
        elif self.__is_last:
            self.unbind("ctrl+down")

    def is_valid(self) -> bool:
        return self.__idx < self.__operations_count

    def get_operation_index(self) -> str:
        return f"{self.__idx + 1}." if self.is_valid() else "?"

    def get_operation_name(self) -> str:
        return humanize_operation_name(self.operation) if self.is_valid() else "?"

    def action_select_previous(self) -> None:
        self.post_message(self.Focus(target_idx=self.__idx - 1))

    def action_select_next(self) -> None:
        self.post_message(self.Focus(target_idx=self.__idx + 1))

    def get_operation_details(self) -> str:
        return humanize_operation_details(self.operation) if self.is_valid() else "?"

    @property
    def idx(self) -> int:
        return self.__idx

    @property
    def operation(self) -> Operation:
        assert self.is_valid(), "cannot get operation, position is invalid"
        return self.app.world.profile_data.cart[self.__idx]

    @property
    def __operations_count(self) -> int:
        return len(self.app.world.profile_data.cart)

    @property
    def __is_first(self) -> bool:
        return self.__idx == 0

    @property
    def __is_last(self) -> bool:
        return self.__idx == self.__operations_count - 1

    @on(CliveButton.Pressed, "#move-up-button")
    def move_up(self) -> None:
        self.post_message(self.Move(from_idx=self.__idx, to_idx=self.__idx - 1))

    @on(CliveButton.Pressed, "#move-down-button")
    def move_down(self) -> None:
        self.post_message(self.Move(from_idx=self.__idx, to_idx=self.__idx + 1))

    @on(CliveButton.Pressed, "#delete-button")
    def delete(self) -> None:
        self.post_message(self.Delete(self))

    @on(Move)
    def move_item(self, event: CartItem.Move) -> None:
        if event.to_idx == self.__idx:
            self.__idx = event.from_idx
        self.app.trigger_profile_data_watchers()


class CartHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=f"{ODD_CLASS_NAME} index")
        yield Static("Operation type", classes=f"{EVEN_CLASS_NAME} operation-type")
        yield Static("Operation details", classes=f"{ODD_CLASS_NAME} operation-details")
        yield Static("Actions", classes=f"{EVEN_CLASS_NAME} actions")


class CartTable(CliveCheckerboardTable):
    """Table with CartItems."""

    def __init__(self) -> None:
        super().__init__(Static(""), CartHeader())

    def create_static_rows(self, start_index: int = 0, end_index: int | None = None) -> list[CartItem]:
        if end_index:
            assert (
                end_index <= len(self.app.world.profile_data.cart) - 1
            ), "End index is greater than cart's last item index"
        return [
            CartItem(idx)
            for idx in range(start_index, len(self.app.world.profile_data.cart) if end_index is None else end_index + 1)
        ]


class Cart(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f9", "clear_all", "Clear all"),
        Binding("f6", "summary", "Summary"),
    ]
    BIG_TITLE = "operations cart"

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with self.__scrollable_part:
            yield CartTable()

    async def __rebuild_items(self, from_index: int = 0, to_index: int | None = None) -> None:
        await self.query_one(CartTable).rebuild(starting_from_element=from_index, ending_with_element=to_index)

    @on(CartItem.Delete)
    async def remove_item(self, event: CartItem.Delete) -> None:
        self.app.world.profile_data.cart.remove(event.widget.operation)
        self.app.trigger_profile_data_watchers()
        await self.__rebuild_items(from_index=event.widget.idx)
        if event.widget.idx == len(self.app.world.profile_data.cart):
            # disable last ButtonMoveDown if only last element was removed
            self.query(ButtonMoveDown)[-1].disabled = True

    @on(CartItem.Move)
    async def move_item(self, event: CartItem.Move) -> None:
        assert event.to_idx >= 0
        assert event.to_idx < len(self.app.world.profile_data.cart)

        self.app.world.profile_data.cart.swap(event.from_idx, event.to_idx)
        self.app.trigger_profile_data_watchers()
        start, end = (event.from_idx, event.to_idx) if event.from_idx < event.to_idx else (event.to_idx, event.from_idx)
        await self.__rebuild_items(from_index=start, to_index=end)

        # focus item that was moved
        for cart_item in self.query(CartItem):
            if event.to_idx == cart_item.idx:
                self.app.set_focus(cart_item)

    @on(CartItem.Focus)
    def focus_item(self, event: CartItem.Focus) -> None:
        for cart_item in self.query(CartItem):
            if event.target_idx == cart_item.idx:
                self.app.set_focus(cart_item)

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummaryFromCart())

    async def action_clear_all(self) -> None:
        self.app.world.profile_data.cart.clear()
        self.app.trigger_profile_data_watchers()
        await self.__rebuild_items()
