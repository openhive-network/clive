from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import DOMQuery, NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static
from typing_extensions import Self

from clive.__private.core.formatters.humanize import humanize_operation_details, humanize_operation_name
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_basic import (
    CLIVE_EVEN_CLASS_NAME,
    CLIVE_ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_basic.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import OperationBase


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


class CartItem(CliveCheckerboardTableRow, CliveWidget):
    """Row of CartTable."""

    BINDINGS = [
        Binding("ctrl+up", "select_previous", "Prev"),
        Binding("ctrl+down", "select_next", "Next"),
    ]

    operation_index: int = reactive(0, init=False)  # type: ignore[assignment]

    @dataclass
    class Delete(Message):
        widget: CartItem

    @dataclass
    class Move(Message):
        from_index: int
        to_index: int

    @dataclass
    class Focus(Message):
        """Message sent when other CartItem should be focused."""

        target_index: int

    def __init__(self, operation_index: int) -> None:
        assert self._is_operation_index_valid(operation_index), "During construction, operation index has to be valid"
        self._operation_index = operation_index

        self._is_already_deleted = False
        """This could be a situation where the user is trying to delete an operation that is already deleted
        (textual has not yet deleted the widget visually). This situation is possible if the user clicks so quickly
        to remove an operation and there are a large number of operations in the shopping basket."""

        self._is_already_moving = False
        """Used to prevent user from moving item when the previous move is not finished yet."""

        super().__init__(*self._create_cells())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operation_index={self._operation_index})"

    @property
    def operation_number_cell(self) -> CliveCheckerBoardTableCell:
        return self.query(CliveCheckerBoardTableCell).first()

    @property
    def button_move_up(self) -> ButtonMoveUp:
        return self.query_one(ButtonMoveUp)

    @property
    def button_move_down(self) -> ButtonMoveDown:
        return self.query_one(ButtonMoveDown)

    @property
    def button_delete(self) -> ButtonDelete:
        return self.query_one(ButtonDelete)

    @property
    def operation(self) -> OperationBase:
        assert self._is_operation_index_valid(self._operation_index), "Cannot get operation, position is invalid."
        return self.profile.cart[self._operation_index]

    @property
    def operations_amount(self) -> int:
        return len(self.profile.cart)

    @property
    def is_first(self) -> bool:
        return self._operation_index == 0

    @property
    def is_last(self) -> bool:
        return self._operation_index == self.operations_amount - 1

    def on_mount(self) -> None:
        self.operation_index = self._operation_index

        if self.is_first:
            self.unbind("ctrl+up")
        elif self.is_last:
            self.unbind("ctrl+down")

    def watch_operation_index(self, value: int) -> None:
        assert self._is_operation_index_valid(value), "Operation index is invalid when trying to update."
        self._operation_index = value
        self.operation_number_cell.update_content(self.humanize_operation_number())

    def humanize_operation_number(self) -> str:
        return f"{self._operation_index + 1}."

    def humanize_operation_name(self) -> str:
        return humanize_operation_name(self.operation)

    def humanize_operation_details(self) -> str:
        return humanize_operation_details(self.operation)

    def action_select_previous(self) -> None:
        self.post_message(self.Focus(target_index=self._operation_index - 1))

    def action_select_next(self) -> None:
        self.post_message(self.Focus(target_index=self._operation_index + 1))

    def focus(self, _: bool = True) -> Self:  # noqa: FBT001, FBT002
        def focus_first_focusable_button() -> None:
            buttons = self.query(CliveButton)
            for button in buttons:
                if button.focusable:
                    button.focus()
                    break

        focused = self.app.focused
        if not focused:
            return self

        assert focused.id, "Previously focused widget has no id!"
        try:
            previous = self.get_widget_by_id(focused.id, CliveButton)
        except NoMatches:
            focus_first_focusable_button()
            return self

        if previous.focusable:
            # Focus button that was focused before
            previous.focus()
        else:
            focus_first_focusable_button()
        return self

    def unset_moving_flag(self) -> None:
        self._is_already_moving = False

    @on(CliveButton.Pressed, "#move-up-button")
    def move_up(self) -> None:
        self._move("up")

    @on(CliveButton.Pressed, "#move-down-button")
    def move_down(self) -> None:
        self._move("down")

    @on(CliveButton.Pressed, "#delete-button")
    def delete(self) -> None:
        if self._is_already_deleted:
            return

        self._is_already_deleted = True
        self.post_message(self.Delete(self))

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(self.humanize_operation_number()),
            CliveCheckerBoardTableCell(self.humanize_operation_name(), classes="operation-name"),
            CliveCheckerBoardTableCell(self.humanize_operation_details(), classes="operation-details"),
            CliveCheckerBoardTableCell(self._create_buttons_container(), classes="actions"),
        ]

    def _create_buttons_container(self) -> Horizontal:
        button_move_up = ButtonMoveUp(disabled=self.is_first)
        button_move_down = ButtonMoveDown(disabled=self.is_last)
        button_delete = ButtonDelete()
        return Horizontal(button_move_up, button_move_down, button_delete)

    def _is_operation_index_valid(self, value: int) -> bool:
        return value < self.operations_amount

    def _move(self, direction: Literal["up", "down"]) -> None:
        if self._is_already_moving:
            return
        self._is_already_moving = True
        index_change = -1 if direction == "up" else 1
        self.post_message(self.Move(from_index=self._operation_index, to_index=self._operation_index + index_change))


class CartHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=CLIVE_ODD_CLASS_NAME)
        yield Static("Operation type", classes=f"{CLIVE_EVEN_CLASS_NAME} operation-name")
        yield Static("Operation details", classes=f"{CLIVE_ODD_CLASS_NAME} operation-details")
        yield Static("Actions", classes=f"{CLIVE_EVEN_CLASS_NAME} actions")


class CartTable(CliveCheckerboardTable):
    """Table with CartItems."""

    def __init__(self) -> None:
        super().__init__(header=CartHeader())

    @property
    def _cart_items(self) -> DOMQuery[CartItem]:
        return self.query(CartItem)

    @property
    def _has_cart_items(self) -> bool:
        return bool(self._cart_items)

    def create_static_rows(self) -> list[CartItem]:
        return [CartItem(index) for index in range(len(self.profile.cart))]

    @on(CartItem.Delete)
    async def remove_item(self, event: CartItem.Delete) -> None:
        item_to_remove = event.widget
        with self.app.batch_update():
            self._focus_appropriate_item_on_deletion(item_to_remove)
            await item_to_remove.remove()
            if self._has_cart_items:
                self._update_cart_items_on_deletion(removed_item=item_to_remove)
                self._disable_appropriate_button_on_deletion(removed_item=item_to_remove)
        self.profile.cart.remove(item_to_remove.operation)
        self.app.trigger_profile_watchers()

    @on(CartItem.Move)
    async def move_item(self, event: CartItem.Move) -> None:
        from_index = event.from_index
        to_index = event.to_index

        assert to_index >= 0, "Item cannot be moved to id lower than 0."
        assert to_index < len(self.profile.cart), "Item cannot be moved to id greater than cart length."

        with self.app.batch_update():
            self._update_values_of_swapped_rows(from_index=from_index, to_index=to_index)
            self._focus_item_on_move(to_index)
            self._unset_moving_flags()

        self.profile.cart.swap(from_index, to_index)
        self.app.trigger_profile_watchers()

    @on(CartItem.Focus)
    def focus_item(self, event: CartItem.Focus) -> None:
        for cart_item in self._cart_items:
            if event.target_index == cart_item.operation_index:
                cart_item.focus()

    def _update_cart_items_on_deletion(self, removed_item: CartItem) -> None:
        def update_indexes() -> None:
            for cart_item in cart_items_to_update:
                cart_item.operation_index = cart_item.operation_index - 1

        start_index = removed_item.operation_index
        cart_items_to_update = self._cart_items[start_index:]
        update_indexes()
        self._set_evenness_styles(cart_items_to_update, starting_index=start_index)

    def _disable_appropriate_button_on_deletion(self, removed_item: CartItem) -> None:
        if removed_item.is_first:
            self._cart_items.first().button_move_up.disabled = True
        elif removed_item.is_last:
            self._cart_items.last().button_move_down.disabled = True

    def _focus_appropriate_item_on_deletion(self, item_to_remove: CartItem) -> None:
        cart_items = self._cart_items
        if len(cart_items) < 2:  # noqa: PLR2004
            # There is no need for special handling, last one will be focused
            return

        if item_to_remove.is_last:
            second_last_cart_item_index = -2
            cart_item_to_focus = cart_items[second_last_cart_item_index]
        else:
            next_cart_item_index = item_to_remove.operation_index + 1
            cart_item_to_focus = cart_items[next_cart_item_index]

        cart_item_to_focus.focus()

    def _update_values_of_swapped_rows(self, from_index: int, to_index: int) -> None:
        def extract_cells_and_data(row_index: int) -> tuple[list[CliveCheckerBoardTableCell], list[str]]:
            row = self._cart_items[row_index]
            cells = row.query(CliveCheckerBoardTableCell)[1:-1]  # Skip "operation number" and "buttons container" cells
            data: list[str] = []
            for cell in cells:
                content = cell.content
                assert isinstance(content, str), f"Cell content is not a string: {content}"
                data.append(content)
            return list(cells), data

        def swap_cell_data(source_cells: list[CliveCheckerBoardTableCell], target_data: list[str]) -> None:
            for cell, value in zip(source_cells, target_data):
                cell.update_content(value)

        from_cells, from_data = extract_cells_and_data(from_index)
        to_cells, to_data = extract_cells_and_data(to_index)

        swap_cell_data(to_cells, from_data)
        swap_cell_data(from_cells, to_data)

    def _focus_item_on_move(self, target_index: int) -> None:
        for cart_item in self._cart_items:
            if target_index == cart_item.operation_index:
                cart_item.focus()
                break

    def _unset_moving_flags(self) -> None:
        for cart_item in self._cart_items:
            cart_item.unset_moving_flag()


class Cart(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f6", "summary", "Summary"),
    ]
    BIG_TITLE = "operations cart"

    def create_main_panel(self) -> ComposeResult:
        with ScrollablePart():
            yield CartTable()

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummaryFromCart())
