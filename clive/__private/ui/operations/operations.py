from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Tab, Tabs

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.operations_list import FINANCIAL_OPERATIONS
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.operations.operation_base import OperationBase


class OperationButton(CliveButton):
    def __init__(self, label: TextType, operation_screen: type[OperationBase]) -> None:
        super().__init__(label)
        self.operation_screen = operation_screen


class OperationTab(Tab):
    """A tab that knows which container of operations is assigned to"""

    def __init__(self, label: str, *, container: str, id_: str | None = None):
        super().__init__(label, id=id_)
        self.container = container


class FinancialOperations(Container):
    """Container used to store all financial operations"""


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        yield Tabs(
            OperationTab("Financial", container="FinancialOperations", id_="financial-tab"),
            Tab("Social", id="social-tab"),
            Tab("Governance", id="governance-tab"),
            Tab("Account management", id="account-management-tab"),
        )
        with FinancialOperations(id="financial-operations"):
            yield OperationButton("TRANSFER", FINANCIAL_OPERATIONS[0])

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        container: FinancialOperations = self.query_one(FinancialOperations)

        if event.tab.id == "financial-tab":
            container.visible = True
        else:
            container.visible = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        self.app.push_screen(button.operation_screen())

    def action_cart(self) -> None:
        if not self.app.world.profile_data.cart:
            Notification("There are no operations in the cart! Cannot continue.", category="warning").show()
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
