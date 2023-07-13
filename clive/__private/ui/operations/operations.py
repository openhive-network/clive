from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.operations_list import (
    FINANCIAL_OPERATIONS,
    GOVERNANCE_OPERATIONS,
    SOCIAL_OPERATIONS,
)
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult
    from textual.widgets import Button

    from clive.__private.ui.operations.operation_base import OperationBase


class OperationButton(CliveButton):
    def __init__(self, label: TextType, operation_screen: type[OperationBase]) -> None:
        super().__init__(label)
        self.operation_screen = operation_screen


class OperationsScroll(VerticalScroll):
    """Container used to scroll through the operations list"""


class MainScroll(VerticalScroll):
    """Container used to scroll through the all screen"""


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with MainScroll():
            with Vertical():
                yield BigTitle("SOCIAL OPERATIONS")
                with Container(classes="social-operations"):
                    for operation in SOCIAL_OPERATIONS:
                        yield OperationButton(self.__humanize_class_name(operation), operation)
                yield BigTitle("GOVERNANCE OPERATIONS")
                with OperationsScroll(classes="operations-scroll"):
                    for operation in GOVERNANCE_OPERATIONS:
                        yield OperationButton(self.__humanize_class_name(operation), operation)
            with Vertical(classes="seperator"):
                yield BigTitle("FINANCIAL OPERATIONS")
                with OperationsScroll(classes="operations-scroll"):
                    for operation in FINANCIAL_OPERATIONS:
                        yield OperationButton(self.__humanize_class_name(operation), operation)
                yield BigTitle("CATEGORIES DESCRIPTION")
                with Container(classes="categories-description"):
                    pass

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
