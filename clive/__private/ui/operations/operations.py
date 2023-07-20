from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, TabbedContent, TabPane

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.operations_list import FINANCIAL_OPERATIONS
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen


class OperationButton(CliveButton):
    def __init__(self, label: TextType, operation_screen: type[OperationBaseScreen] | None) -> None:
        super().__init__(label)
        self.operation_screen = operation_screen


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent(initial="financial"):
            with TabPane("Financial", id="financial"):
                yield OperationButton("TRANSFER", FINANCIAL_OPERATIONS[0])
                yield OperationButton("HIVE POWER MANAGEMENT", None)
                yield OperationButton("CONVERT", None)
                yield OperationButton("SAVING", None)
            with TabPane("Social", id="social"):
                yield OperationButton("SOCIAL OPERATIONS", None)
            with TabPane("Governance", id="governance"):
                yield OperationButton("GOVERNANCE OPERATIONS", None)
            with TabPane("Account management", id="account-management"):
                yield OperationButton("ACCOUNT MANAGEMENT OPERATIONS", None)

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        if not button.operation_screen:
            Notification("Not implemented yet", category="warning").show()
            return
        self.app.push_screen(button.operation_screen())

    def action_cart(self) -> None:
        if not self.app.world.profile_data.cart:
            Notification("There are no operations in the cart! Cannot continue.", category="warning").show()
            return

        self.app.push_screen(Cart())
