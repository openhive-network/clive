from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Static

from clive.ui.operations.tranaction_summary import TransactionSummary
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.dynamic_label import DynamicLabel
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.operation import Operation
    from clive.storage.mock_database import ProfileData


class DynamicColumn(DynamicLabel):
    """Column with dynamic content"""


class StaticColumn(Static):
    """Column with static content"""


class ColumnLayout(Static):
    """This class holds column order"""


class ButtonMoveUp(Button):
    """Button used for moving the operation up in the cart"""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("🔼", id="move-up-button", disabled=disabled)


class ButtonMoveDown(Button):
    """Button used for moving the operation down in the cart"""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("🔽", id="move-down-button", disabled=disabled)


class ButtonDelete(Button):
    """Button used for removing the operation from cart"""

    def __init__(self) -> None:
        super().__init__("🗑️", id="delete-button")


class StaticPart(Static):
    """Container for the static part of the screen - title, global buttons and table header"""


class ScrollablePart(Container):
    """Container used for holding operation items"""


class DetailedCartOperation(ColumnLayout, CliveWidget):
    class Deleted(Message):
        def __init__(self, deleted: Operation) -> None:
            self.deleted = deleted
            super().__init__()

    class Move(Message):
        def __init__(self, from_idx: int, to_idx: int) -> None:
            self.from_idx = from_idx
            self.to_idx = to_idx
            super().__init__()

    def __init__(self, operation_idx: int) -> None:
        self.__idx = operation_idx
        assert self.is_valid(), "During construction, index has to be valid"
        super().__init__()

    def is_valid(self) -> bool:
        return self.__idx < self.__operations_count

    def compose(self) -> ComposeResult:
        def operation_index(_: ProfileData) -> str:
            if self.is_valid():
                return f"{self.__idx + 1}."
            return ""

        def operation_name(_: ProfileData) -> str:
            if self.is_valid():
                return self.__operation.type_
            return ""

        def operation_details(_: ProfileData) -> str:
            if self.is_valid():
                return self.__operation.pretty()
            return ""

        yield DynamicColumn(
            self.app, "profile_data", operation_index, id_="operation_position_in_trx", classes="cell cell-middle"
        )
        yield DynamicColumn(
            self.app, "profile_data", operation_name, id_="operation_type", classes="cell cell-variant cell-middle"
        )
        yield DynamicColumn(self.app, "profile_data", operation_details, id_="operation_details", classes="cell")
        yield ButtonMoveUp(disabled=self.__is_first)
        yield ButtonMoveDown(disabled=self.__is_last)
        yield ButtonDelete()

    @property
    def idx(self) -> int:
        return self.__idx

    @property
    def __operations_count(self) -> int:
        return len(self.app.profile_data.operations_cart)

    @property
    def __operation(self) -> Operation:
        assert self.is_valid(), "cannot get operation, position is invalid"
        return self.app.profile_data.operations_cart[self.__idx]

    @property
    def __is_first(self) -> bool:
        return self.__idx == 0

    @property
    def __is_last(self) -> bool:
        return self.__idx == self.__operations_count - 1

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "delete-button":
            self.post_message(self.Deleted(self.__operation))
        elif event.button.id == "move-up-button":
            self.post_message(self.Move(self.__idx, self.__idx - 1))
        elif event.button.id == "move-down-button":
            self.post_message(self.Move(self.__idx, self.__idx + 1))

    def on_detailed_cart_operation_move(self, event: DetailedCartOperation.Move) -> None:
        if event.to_idx == self.__idx:
            self.__idx = event.from_idx
        self.app.update_reactive("profile_data")


class CartOperationsHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="operation_position_in_trx", classes="cell cell-middle")
        yield StaticColumn("Operation Type", id="operation_type", classes="cell cell-variant cell-middle")
        yield StaticColumn("Operation Details", id="operation_details", classes="cell cell-middle")
        yield StaticColumn("Move Up", classes="cell cell-variant cell-middle")
        yield StaticColumn("Move Down", classes="cell cell-middle")
        yield StaticColumn("Delete", classes="cell cell-variant cell-middle")


class Cart(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f9", "clear_all", "Clear all"),
        Binding("f10", "summary", "Summary"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            with StaticPart():
                yield BigTitle("operations cart")
                yield CartOperationsHeader()

            with self.__scrollable_part:
                for idx, _ in enumerate(self.app.profile_data.operations_cart):
                    yield DetailedCartOperation(idx)

            yield Static()

    def on_detailed_cart_operation_deleted(self, event: DetailedCartOperation.Deleted) -> None:
        widget = self.query(DetailedCartOperation).last()
        self.app.profile_data.operations_cart.remove(event.deleted)
        widget.add_class("deleted")
        widget.remove()
        self.app.update_reactive("profile_data")

    def on_detailed_cart_operation_move(self, event: DetailedCartOperation.Move) -> None:
        assert event.to_idx >= 0 and event.to_idx < len(self.app.profile_data.operations_cart)

        self.__swap_operations(event.from_idx, event.to_idx)
        self.app.update_reactive("profile_data")

    def __swap_operations(self, first_index: int, second_index: int) -> None:
        self.app.profile_data.operations_cart[first_index], self.app.profile_data.operations_cart[second_index] = (
            self.app.profile_data.operations_cart[second_index],
            self.app.profile_data.operations_cart[first_index],
        )

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummary())

    def action_clear_all(self) -> None:
        self.app.profile_data.operations_cart.clear()
        self.app.update_reactive("profile_data")
        self.__scrollable_part.add_class("-hidden")
