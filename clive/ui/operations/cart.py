from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container, Horizontal
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


class ButtonsContainer(Horizontal):
    """Container for the buttons"""


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


class ButtonSummary(Button):
    """Button used for navigating to the operations summary"""

    def __init__(self) -> None:
        super().__init__("📝 Summary", id="summary-button")


class ButtonOperations(Button):
    """Button used for navigating to the operations choice screen"""

    def __init__(self) -> None:
        super().__init__("🔙 Add more ops", id="operations-button")


class StaticPart(Static):
    """Container for the static part of the screen - title, global buttons and table header"""


class ScrollablePart(Container):
    """Container used for holding operation items"""


class DetailedCartOperation(ColumnLayout, CliveWidget):
    def __init__(self, operation: Operation) -> None:
        self.__operation = operation
        self.__operation_idx = self.app.profile_data.operations_cart.index(operation)
        assert self.is_valid(), "During construction, index has to be valid"
        super().__init__()

    def __sync_position(self) -> None:
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

        yield DynamicColumn(self.app, "profile_data", operation_index, id_="operation_position_in_trx", classes="cell")
        yield DynamicColumn(self.app, "profile_data", operation_name, id_="operation_type", classes="cell cell-variant")
        yield DynamicColumn(self.app, "profile_data", operation_details, id_="operation_details", classes="cell")
        yield ButtonMoveUp(disabled=self.__operation_idx == 0)
        yield ButtonMoveDown(disabled=self.__operation_idx >= self.__operations_count)
        yield ButtonDelete()

    @property
    def __operations_count(self) -> int:
        return len(self.app.profile_data.operations_cart)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "delete-button":
            self.app.profile_data.operations_cart.remove(self.__operation)
            self.add_class("deleted")
            self.remove()
        elif event.button.id == "move-up-button":
            changed = True
            assert self.__operation_idx != 0, "can't move up first operation"
            (
                self.app.profile_data.operations_cart[self.__operation_idx - 1],
                self.app.profile_data.operations_cart[self.__operation_idx],
            ) = (
                self.app.profile_data.operations_cart[self.__operation_idx],
                self.app.profile_data.operations_cart[self.__operation_idx - 1],
            )
        elif event.button.id == "move-down-button":
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
        yield StaticColumn("No.", id="operation_position_in_trx", classes="cell")
        yield StaticColumn("Operation Type", id="operation_type", classes="cell cell-variant")
        yield StaticColumn("Operation Details", id="operation_details", classes="cell")
        yield StaticColumn("Move Up", classes="cell cell-variant")
        yield StaticColumn("Move Down", classes="cell")
        yield StaticColumn("Delete", classes="cell cell-variant")


class Cart(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Operations"),
        Binding("f1", "summary", "Summary"),
    ]

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            with StaticPart():
                yield BigTitle("operations cart")

                with ButtonsContainer():
                    yield ButtonOperations()
                    yield ButtonSummary()

                yield CartOperationsHeader()

            with ScrollablePart():
                for operation in self.app.profile_data.operations_cart:
                    yield DetailedCartOperation(operation)

            yield Static()

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummary())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "summary-button":
            self.action_summary()
        elif event.button.id == "operations-button":
            self.app.pop_screen()
