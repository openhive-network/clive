from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import TabPane

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations import Governance, HivePowerManagement, Savings, TransferToAccount
from clive.__private.ui.operations.bindings import CartBinding
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.transaction_summary import TransactionSummaryFromFile
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.not_implemented_yet import NotImplementedYetButton, NotImplementedYetTabPane
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.select_file import SelectFile

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen


class OperationButton(CliveButton):
    def __init__(self, label: TextType, operation_screen: type[OperationBaseScreen]) -> None:
        super().__init__(label)
        self.operation_screen = operation_screen


class Operations(CartBasedScreen, CartBinding):
    CSS_PATH = [
        *CartBasedScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    BINDINGS = [
        *CartBinding.BINDINGS,
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f3", "load_transaction_from_file", "Load from file"),
    ]

    def create_left_panel(self) -> ComposeResult:
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

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(CliveTabbedContent).active = tab

    def action_load_transaction_from_file(self) -> None:
        self.app.push_screen(SelectFile())
        self.notify("Your cart will remain unchanged.")

    @on(OperationButton.Pressed)
    def push_operation_screen(self, event: OperationButton.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        self.app.push_screen(button.operation_screen())

    @on(SelectFile.Saved)
    async def load_transaction_from_file(self, event: SelectFile.Saved) -> None:
        file_path = event.file_path

        try:
            transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return

        await self.app.push_screen(TransactionSummaryFromFile(transaction, file_path))
