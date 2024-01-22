from __future__ import annotations

from typing import TYPE_CHECKING

import inflection
from textual import on
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import TabPane

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations import Governance, HivePowerManagement, Savings, TransferToAccount
from clive.__private.ui.operations.bindings import CartBinding
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.transaction_summary import TransactionSummaryFromFile
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.select_file import SelectFile

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
    from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen


class OperationButton(CliveButton):
    def __init__(
        self,
        operation_screen: type[OperationBaseScreen | RawOperationBaseScreen] | None,
        *,
        label: TextType | None = None,
    ) -> None:
        if operation_screen is None and label is None:
            raise ValueError("Either `operation_screen` or `label` must be provided!")

        if label is None:
            assert operation_screen is not None
            label = self.__humanize_class_name(operation_screen.__name__)

        super().__init__(label)
        self.operation_screen = operation_screen

    @staticmethod
    def __humanize_class_name(class_name: str) -> str:
        return inflection.humanize(inflection.underscore(class_name))


class ScrollablePart(VerticalScroll, can_focus=False):
    pass


class Operations(CartBasedScreen, CartBinding):
    CSS_PATH = [
        *CartBasedScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    BINDINGS = [
        *CartBinding.BINDINGS,
        Binding("escape", "pop_screen", "Back"),
        Binding("f3", "load_transaction_from_file", "Load from file"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with CliveTabbedContent(initial="financial"):
            with TabPane("Financial", id="financial"), ScrollablePart():
                yield OperationButton(TransferToAccount, label="Transfer")
                yield OperationButton(Savings, label="Saving")
                yield OperationButton(HivePowerManagement, label="Hive power management")
                yield OperationButton(None, label="Convert")
            with TabPane("Social"), ScrollablePart():
                yield OperationButton(None, label="Social operations")
            with TabPane("Governance"), ScrollablePart():
                yield OperationButton(Governance, label="Governance operations")
            with TabPane("Account management"), ScrollablePart():
                yield OperationButton(None, label="Account management operations")

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(CliveTabbedContent).active = tab

    def action_load_transaction_from_file(self) -> None:
        self.app.push_screen(SelectFile())
        self.notify("Your cart will remain unchanged.")

    @on(OperationButton.Pressed)
    def push_operation_screen(self, event: OperationButton.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        if not button.operation_screen:
            self.notify("Not implemented yet!", severity="error")
            return
        self.app.push_screen(button.operation_screen())

    @on(SelectFile.Saved)
    async def load_transaction_from_file(self, event: SelectFile.Saved) -> None:
        file_path = event.file_path

        try:
            transaction = (await self.app.world.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return

        await self.app.push_screen(TransactionSummaryFromFile(transaction, file_path))
