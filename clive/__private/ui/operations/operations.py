from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding
from textual.widgets import Static, TabbedContent

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.operations_list import FINANCIAL_OPERATIONS, RAW_OPERATIONS
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
    from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen


class OperationButton(CliveButton):
    def __init__(
        self, label: TextType, operation_screen: type[OperationBaseScreen | RawOperationBaseScreen] | None
    ) -> None:
        super().__init__(label)
        self.operation_screen = operation_screen


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent(initial="financial"):
            with ScrollableTabPane("Financial", id="financial"):
                yield OperationButton("TRANSFER", FINANCIAL_OPERATIONS[0])
                yield OperationButton("HIVE POWER MANAGEMENT", None)
                yield OperationButton("CONVERT", None)
                yield OperationButton("SAVING", None)
            with ScrollableTabPane("Social"):
                yield OperationButton("SOCIAL OPERATIONS", None)
            with ScrollableTabPane("Governance"):
                yield OperationButton("GOVERNANCE OPERATIONS", None)
            with ScrollableTabPane("Account management"):
                yield OperationButton("ACCOUNT MANAGEMENT OPERATIONS", None)
            with ScrollableTabPane("Raw"):
                yield Static("select one of the following operation:", id="hint")
                for operation in RAW_OPERATIONS:
                    yield OperationButton(self.__humanize_class_name(operation), operation)

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab

    @on(OperationButton.Pressed)
    def push_operation_screen(self, event: OperationButton.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        if not button.operation_screen:
            self.notify("Not implemented yet!", severity="error")
            return
        self.app.push_screen(button.operation_screen())

    def action_cart(self) -> None:
        if not self.app.world.profile_data.cart:
            self.notify("There are no operations in the cart! Cannot continue.", severity="warning")
            return

        self.app.push_screen(Cart())

    @staticmethod
    def __humanize_class_name(type_: type[Any]) -> str:
        result = ""

        class_name = type_.__name__.replace("_", "")
        for char in class_name:
            if char.isupper():
                result += " "
            result += char.lower()
        return result.strip().title()
