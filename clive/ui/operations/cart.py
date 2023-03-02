from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, Static

from clive.ui.operations.tranaction_summary import TransactionSummary
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.dynamic_label import DynamicLabel
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import ProfileData


class DynamicColumn(DynamicLabel):
    """Column with dynamic content"""


class StaticColumn(Static):
    """Column with static content"""


class ColumnLayout(Static):
    """This class holds column order"""


odd = "OddColumn"
even = "EvenColumn"


class DetailedCartOperation(ColumnLayout, CliveWidget):
    def __init__(self, operation_idx: int) -> None:
        self.__operation_idx = operation_idx
        assert self.is_valid(), "During construction, index has to be valid"
        self.__operation = self.app.profile_data.operations_cart[self.__operation_idx]
        super().__init__()

    def __sync_position(self) -> None:
        self.log.debug("__sync_position")

        if self.is_valid() and self.app.profile_data.operations_cart[self.__operation_idx] == self.__operation:
            return

        if self.__operation in self.app.profile_data.operations_cart:
            self.__operation_idx = self.app.profile_data.operations_cart.index(self.__operation)
        elif self.is_valid():
            self.__operation = self.app.profile_data.operations_cart[self.__operation_idx]

    def on_mount(self) -> None:
        self.watch(self.app, "profile_data", self.__sync_position)

    def is_valid(self) -> bool:
        return self.__operation_idx < self.__operations_count

    def compose(self) -> ComposeResult:
        def operation_index(_: ProfileData) -> str:
            if self.is_valid():
                return f"{self.__operation_idx + 1}."
            return "⌛"

        def operation_name(_: ProfileData) -> str:
            if self.is_valid():
                return self.__operation.type_
            return "⌛"

        def operation_details(_: ProfileData) -> str:
            if self.is_valid():
                return self.__operation.as_json()
            return "⌛"

        yield DynamicColumn(self.app, "profile_data", operation_index, id_="operation_position_in_trx", classes=even)
        yield DynamicColumn(self.app, "profile_data", operation_name, id_="operation_type", classes=odd)
        yield DynamicColumn(self.app, "profile_data", operation_details, id_="operation_details", classes=even)
        yield Button("⬆️", id="move_operation_up_button", classes=odd, disabled=(self.__operation_idx == 0))
        yield Button(
            "⬇️",
            id="move_operation_down_button",
            classes=odd,
            disabled=(self.__operation_idx >= self.__operations_count),
        )
        yield Button("🗑️", id="remove_operation_button", classes=odd)

    @property
    def __operations_count(self) -> int:
        return len(self.app.profile_data.operations_cart)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        changed = False
        if event.button.id == "remove_operation_button":
            changed = True
            self.app.profile_data.operations_cart.remove(self.__operation)
            self.add_class("deleted")
            self.remove()
        elif event.button.id == "move_operation_up_button":
            changed = True
            assert self.__operation_idx != 0, "can't move up first operation"
            (
                self.app.profile_data.operations_cart[self.__operation_idx - 1],
                self.app.profile_data.operations_cart[self.__operation_idx],
            ) = (
                self.app.profile_data.operations_cart[self.__operation_idx],
                self.app.profile_data.operations_cart[self.__operation_idx - 1],
            )
        elif event.button.id == "move_operation_down_button":
            changed = True
            assert self.__operation_idx < self.__operations_count - 1
            (
                self.app.profile_data.operations_cart[self.__operation_idx + 1],
                self.app.profile_data.operations_cart[self.__operation_idx],
            ) = (
                self.app.profile_data.operations_cart[self.__operation_idx],
                self.app.profile_data.operations_cart[self.__operation_idx + 1],
            )
        if changed:
            self.app.update_reactive("profile_data")


class CartOperationsHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="operation_position_in_trx", classes=even)
        yield StaticColumn("Operation Type", id="operation_type", classes=odd)
        yield StaticColumn("Operation Details", id="operation_details", classes=even)
        yield StaticColumn("Move Up", classes=odd)
        yield StaticColumn("Move Down", classes=even)
        yield StaticColumn("Delete", classes=odd)


class CartOperationTitle(Static):
    def compose(self) -> ComposeResult:
        yield BigTitle("staged ops", id="cart_operations_title_label")


class Cart(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Operations"),
        Binding("f1", "summary", "Summary"),
    ]

    def create_main_panel(self) -> ComposeResult:
        yield CartOperationTitle()
        yield CartOperationsHeader()

        self.__mount_point_for_ops = ViewBag()
        with self.__mount_point_for_ops:
            for i, _ in enumerate(self.app.profile_data.operations_cart):
                yield DetailedCartOperation(i)

        yield Button("📦️ summary", id="cart_operations_go_to_summary")
        yield Button("+ add more operations", id="cart_operations_more_ops")

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummary())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "cart_operations_go_to_summary":
            self.action_summary()
        elif event.button.id == "cart_operations_more_ops":
            self.app.pop_screen()
