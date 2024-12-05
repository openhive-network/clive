from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import TabPane

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.screens.operations.bindings import TransactionSummaryBinding
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_basic import CliveTabbedContent
from clive.__private.ui.widgets.not_implemented_yet import NotImplementedYetButton, NotImplementedYetTabPane
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen


class OperationButton(CliveButton):
    def __init__(self, label: TextType, operation_screen: type[OperationBaseScreen]) -> None:
        super().__init__(label, classes="operation-button")
        self.operation_screen = operation_screen


class Operations(CartBasedScreen, TransactionSummaryBinding):
    CSS_PATH = [
        *CartBasedScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    BINDINGS = [
        *TransactionSummaryBinding.BINDINGS,
        Binding("escape", "app.pop_screen", "Back"),
        Binding("ctrl+t", "transaction_summary", "Transaction summary"),
    ]

    def create_left_panel(self) -> ComposeResult:
        from clive.__private.ui.screens.operations import Governance, HivePowerManagement, Savings, TransferToAccount

        with CliveTabbedContent(initial="financial"):
            with TabPane("Financial", id="financial"), ScrollablePart():
                yield OperationButton("Transfer", TransferToAccount)
                yield OperationButton("Savings", Savings)
                yield OperationButton("Hive power management", HivePowerManagement)
                yield NotImplementedYetButton("Convert")
            with NotImplementedYetTabPane("Social"), ScrollablePart():
                yield NotImplementedYetButton("Social operations")
            with TabPane("Governance"), ScrollablePart():
                yield OperationButton("Governance", Governance)
            with NotImplementedYetTabPane("Account management"), ScrollablePart():
                yield NotImplementedYetButton("Account management operations")

    @on(OperationButton.Pressed, ".operation-button")
    def push_operation_screen(self, event: OperationButton.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        self.app.push_screen(button.operation_screen())
