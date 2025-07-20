from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.containers import Horizontal
from textual.content import Content
from textual.events import Mount
from textual.message import Message
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME
from clive.__private.core.constants.tui.texts import LOADING_TEXT
from clive.__private.core.formatters.humanize import humanize_operation_details, humanize_operation_name
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.confirm_invalidate_signatures_dialog import ConfirmInvalidateSignaturesDialog
from clive.__private.ui.dialogs.raw_json_dialog import RawJsonDialog
from clive.__private.ui.widgets.buttons import CliveButton, RemoveButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.no_content_available import NoContentAvailable

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.css.query import DOMQuery

    from clive.__private.models import Transaction
    from clive.__private.models.schemas import OperationUnion
    from clive.__private.ui.widgets.clive_basic.clive_checkerboard_table import CellContent


class MoveUpButton(CliveButton):
    """
    Button used for moving the operation up in the cart.

    Args:
        disabled: Whether the button should be disabled initially.
    """

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↑", id_="move-up-button", disabled=disabled)


class MoveDownButton(CliveButton):
    """
    Button used for moving the operation down in the cart.

    Args:
        disabled: Whether the button should be disabled initially.
    """

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↓", id_="move-down-button", disabled=disabled)


class RawJsonButton(CliveButton):
    """Button used for displaying raw json of single operation added to cart."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that raw json button was pressed."""

    def __init__(self) -> None:
        super().__init__("JSON", id_="raw-json-button")


@dataclass
class CartItemsActionManager:
    """Object used for disabling actions like move/delete on cart items while another action is in progress."""

    _is_action_disabled: bool = False

    @property
    def is_action_disabled(self) -> bool:
        return self._is_action_disabled

    def enable_action(self) -> None:
        self._is_action_disabled = False

    def disable_action(self) -> None:
        self._is_action_disabled = True


class CartItem(CliveCheckerboardTableRow, CliveWidget):
    """
    Row of CartTable.

    Args:
        action_manager: Object to manage actions like move/delete.
    """

    @dataclass
    class Delete(Message):
        widget: CartItem

    @dataclass
    class Move(Message):
        from_index: int
        to_index: int

    def __init__(self, action_manager: CartItemsActionManager) -> None:
        super().__init__(*self._create_cells())
        self._action_manager = action_manager

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operation_index={self.operation_index})"

    @property
    def operation_index(self) -> int:
        return self.index

    @property
    def operation_number_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#op-number-cell", CliveCheckerBoardTableCell)

    @property
    def operation_name_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#op-name-cell", CliveCheckerBoardTableCell)

    @property
    def operation_details_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#op-details-cell", CliveCheckerBoardTableCell)

    @property
    def buttons_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#buttons-cell", CliveCheckerBoardTableCell)

    @property
    def button_move_up(self) -> MoveUpButton:
        return self.query_exactly_one(MoveUpButton)

    @property
    def button_move_down(self) -> MoveDownButton:
        return self.query_exactly_one(MoveDownButton)

    @property
    def button_delete(self) -> RemoveButton:
        return self.query_exactly_one(RemoveButton)

    @property
    def operation(self) -> OperationUnion:
        assert self._is_operation_index_valid(self.operation_index), "Cannot get operation, position is invalid."
        return self.profile.operations[self.operation_index]

    @property
    def operations_amount(self) -> int:
        return len(self.profile.transaction)

    @property
    def is_first(self) -> bool:
        return self.operation_index == 0

    @property
    def is_last(self) -> bool:
        return self.operation_index == self.operations_amount - 1

    def humanize_operation_number(self, *, before_removal: bool = False) -> str:
        cart_items = self.operations_amount - 1 if before_removal else self.operations_amount
        return f"{self.operation_index + 1}/{cart_items}"

    def humanize_operation_name(self) -> str:
        return humanize_operation_name(self.operation)

    def humanize_operation_details(self) -> str:
        return humanize_operation_details(self.operation)

    @on(Mount)
    async def update_cells(self) -> None:
        """
        Update content of cells that require row index.

        The cells are initialized with a LOADING_TEXT because of the row index,
        which is assigned automatically later, during row creation. The cells content is
        updated here once the row is fully created and its index becomes available.
        """
        if not self.profile.transaction:
            # There may be a case where the file save / broadcast is executed beforehand, and the operation
            # represented by CartItem is no longer available.
            return

        await self.operation_number_cell.update_content(self.humanize_operation_number())
        await self.operation_name_cell.update_content(self.humanize_operation_name())
        await self.operation_details_cell.update_content(Content(self.humanize_operation_details()))
        await self.buttons_cell.update_content(self._create_buttons_container())

    @on(CliveButton.Pressed, "#move-up-button")
    def move_up(self) -> None:
        self._move("up")

    @on(CliveButton.Pressed, "#move-down-button")
    def move_down(self) -> None:
        self._move("down")

    @on(RemoveButton.Pressed)
    def delete(self) -> None:
        def post_message_and_disable_action() -> None:
            self._action_manager.disable_action()
            self.post_message(self.Delete(self))

        async def cb(confirm: bool | None) -> None:  # noqa: FBT001
            if confirm:
                post_message_and_disable_action()

        if self._action_manager.is_action_disabled:
            return

        if self.profile.transaction.is_signed:
            self.app.push_screen(ConfirmInvalidateSignaturesDialog(), cb)
        else:
            post_message_and_disable_action()

    @on(RawJsonButton.Pressed)
    async def show_raw_json(self) -> None:
        await self.app.push_screen(RawJsonDialog(operation=self.operation))

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(LOADING_TEXT, id_="op-number-cell"),
            CliveCheckerBoardTableCell(LOADING_TEXT, id_="op-name-cell", classes="operation-name"),
            CliveCheckerBoardTableCell(LOADING_TEXT, id_="op-details-cell", classes="operation-details"),
            CliveCheckerBoardTableCell(LOADING_TEXT, id_="buttons-cell", classes="actions"),
        ]

    def _create_buttons_container(self) -> Horizontal:
        button_move_up = MoveUpButton(disabled=self.is_first)
        button_move_down = MoveDownButton(disabled=self.is_last)
        button_delete = RemoveButton()
        button_show_json = RawJsonButton()
        return Horizontal(button_show_json, button_move_up, button_move_down, button_delete)

    def _is_operation_index_valid(self, value: int) -> bool:
        return 0 <= value < self.operations_amount

    def _set_operation_index(self, value: int) -> None:
        assert self._is_operation_index_valid(value), "Operation index was invalid when trying to update."
        self._index = value

    def _move(self, direction: Literal["up", "down"]) -> None:
        def post_message_and_disable_action() -> None:
            self._action_manager.disable_action()
            index_change = -1 if direction == "up" else 1
            self.post_message(self.Move(from_index=self.operation_index, to_index=self.operation_index + index_change))

        async def cb(confirm: bool | None) -> None:  # noqa: FBT001
            if confirm:
                post_message_and_disable_action()

        if self._action_manager.is_action_disabled:
            return

        if self.profile.transaction.is_signed:
            self.app.push_screen(ConfirmInvalidateSignaturesDialog(), cb)
        else:
            post_message_and_disable_action()


class CartHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("Operation type", classes=f"{CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME} operation-name")
        yield Static("Operation details", classes=f"{CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME} operation-details")
        yield Static("Actions", classes=f"{CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME} actions")


class CartTable(CliveCheckerboardTable):
    """
    Table with CartItems.

    Attributes:
        NO_CONTENT_TEXT: Text displayed when there are no items in the cart.
    """

    NO_CONTENT_TEXT = "Cart is empty"

    @dataclass
    class Modified(Message):
        """Message sent when operations in CartTable were reordered or removed."""

        transaction: Transaction

    def __init__(self) -> None:
        super().__init__(header=CartHeader())
        self._cart_items_action_manager = CartItemsActionManager()

    @property
    def _cart_items(self) -> DOMQuery[CartItem]:
        return self.query(CartItem)

    @property
    def _has_cart_items(self) -> bool:
        return bool(self._cart_items)

    def create_static_rows(self) -> list[CartItem]:
        return [CartItem(self._cart_items_action_manager) for _ in self.profile.transaction]

    @on(CartItem.Delete)
    async def remove_item(self, event: CartItem.Delete) -> None:
        item_to_remove = event.widget

        with self.app.batch_update():
            self._focus_appropriate_item_on_deletion(item_to_remove)
            await item_to_remove.remove()
            if self._has_cart_items:
                await self._update_cart_items_on_deletion(removed_item=item_to_remove)
                self._disable_appropriate_button_on_deletion(removed_item=item_to_remove)
            else:
                await self.query_exactly_one(CartHeader).remove()
                await self.mount(NoContentAvailable(self.NO_CONTENT_TEXT))

        modified_transaction = deepcopy(self.profile.transaction)
        modified_transaction.remove_operation(item_to_remove.operation)
        await self.commands.update_transaction_metadata(transaction=modified_transaction)
        if not modified_transaction:
            # if last operation was removed from transaction, reset it
            modified_transaction.reset()
        self._cart_items_action_manager.enable_action()
        self.post_message(self.Modified(modified_transaction))

    @on(CartItem.Move)
    async def move_item(self, event: CartItem.Move) -> None:
        from_index = event.from_index
        to_index = event.to_index

        assert to_index >= 0, "Item cannot be moved to id lower than 0."
        assert to_index < len(self.profile.transaction), "Item cannot be moved to id greater than cart length."

        with self.app.batch_update():
            await self._update_values_of_swapped_rows(from_index=from_index, to_index=to_index)
            self._focus_item_on_move(to_index)

        modified_transaction = deepcopy(self.profile.transaction)
        modified_transaction.swap_operations(from_index, to_index)
        await self.commands.update_transaction_metadata(transaction=modified_transaction)
        self._cart_items_action_manager.enable_action()
        self.post_message(self.Modified(modified_transaction))

    async def _update_cart_items_on_deletion(self, removed_item: CartItem) -> None:
        def update_indexes() -> None:
            for cart_item in cart_items_to_update_index:
                cart_item._set_operation_index(value=cart_item.operation_index - 1)

        async def update_operation_number() -> None:
            """Manually update displayed operation number of all items."""
            for cart_item in all_cart_items:
                await cart_item.operation_number_cell.update_content(
                    cart_item.humanize_operation_number(before_removal=True)
                )

        def update_evenness() -> None:
            self._set_evenness_styles(cart_items_to_update_index, starting_index=start_index)

        all_cart_items = self._cart_items
        start_index = removed_item.operation_index
        cart_items_to_update_index = all_cart_items[start_index:]
        update_indexes()
        update_evenness()
        await update_operation_number()

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

    async def _update_values_of_swapped_rows(self, from_index: int, to_index: int) -> None:
        def extract_cells_and_data(row_index: int) -> tuple[list[CliveCheckerBoardTableCell], list[CellContent]]:
            row = self._cart_items[row_index]
            cells = row.query(CliveCheckerBoardTableCell)[1:-1]  # Skip "operation number" and "buttons container" cells
            data = [cell.content for cell in cells]
            return list(cells), data

        async def swap_cell_data(
            source_cells: list[CliveCheckerBoardTableCell], target_data: list[CellContent]
        ) -> None:
            for cell, value in zip(source_cells, target_data, strict=False):
                await cell.update_content(value)

        from_cells, from_data = extract_cells_and_data(from_index)
        to_cells, to_data = extract_cells_and_data(to_index)

        await swap_cell_data(to_cells, from_data)
        await swap_cell_data(from_cells, to_data)

    def _focus_item_on_move(self, target_index: int) -> None:
        for cart_item in self._cart_items:
            if target_index == cart_item.operation_index:
                cart_item.focus()
                break
