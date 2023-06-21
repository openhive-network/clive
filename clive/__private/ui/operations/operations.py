from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, Static

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.operations_with_buttons_list import OPERATIONS_AND_BUTTONS
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Select one of the following operations:", id="hint")
            yield CliveButton("Transfer to account", id_="account-transfer-button")
            yield CliveButton("Transfer to savings", id_="savings-transfer-button")
            yield CliveButton("Transfer to vesting", id_="vesting-transfer-button")
            yield CliveButton("Vote", id_="vote-button")
            yield CliveButton("Convert", id_="convert-button")
            yield CliveButton("Account witness vote", id_="account-witness-vote-button")
            yield CliveButton("Witness block approve", id_="witness-block-approve-button")
            yield CliveButton("Power up", id_="power-up-button")
            yield CliveButton("Power down", id_="power-down-button")

    def create_operation(self) -> Operation | None:
        """Not implemented here"""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in OPERATIONS_AND_BUTTONS:
            button_id = event.button.id
            self.app.push_screen(OPERATIONS_AND_BUTTONS[button_id]())
        else:
            Notification("Not implemented yet!", category="error").show()

    def action_cart(self) -> None:
        if not self.app.world.profile_data.cart:
            Notification("There are no operations in the cart! Cannot continue.", category="warning").show()
            return

        self.app.push_screen(Cart())
