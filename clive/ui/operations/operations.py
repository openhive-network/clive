from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, Static

from clive.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.ui.operations.transfer_to_account.transfer_to_account import TransferToAccount
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Dashboard"),
        Binding("f1", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Select one of the following operations:", id="hint")
            yield Button("Transfer to account", id="account-transfer-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account-transfer-button":
            self.app.push_screen(TransferToAccount())

    def action_cart(self) -> None:
        self.log("Should go to the cart management screen")
