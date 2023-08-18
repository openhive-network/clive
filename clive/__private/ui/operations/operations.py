from __future__ import annotations

from typing import TYPE_CHECKING

import inflection
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


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent(initial="financial"):
            with ScrollableTabPane("Financial", id="financial"):
                yield OperationButton(FINANCIAL_OPERATIONS[0], label="Transfer")
                yield OperationButton(None, label="Hive power management")
                yield OperationButton(None, label="Convert")
                yield OperationButton(None, label="Saving")
            with ScrollableTabPane("Social"):
                yield OperationButton(None, label="Social operations")
            with ScrollableTabPane("Governance"):
                yield OperationButton(None, label="Governance operations")
            with ScrollableTabPane("Account management"):
                yield OperationButton(None, label="Account management operations")
            yield from self.__create_raw_operations_tab(hide=True)

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

    def __create_raw_operations_tab(self, *, hide: bool = False) -> ComposeResult:
        if hide:
            return []

        with ScrollableTabPane("Raw"):
            yield Static("select one of the following operation:", id="hint")
            for operation in RAW_OPERATIONS:
                yield OperationButton(operation)
