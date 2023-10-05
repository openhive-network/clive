from __future__ import annotations

from textual.binding import Binding

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen


class OperationBaseScreen(CartBasedScreen, AbstractClassMessagePump):
    """Base class for all screens that represent operations."""

    BINDINGS = [Binding("escape", "pop_screen", "Back")]


class SavingsBaseScreen(OperationBaseScreen):
    BINDINGS = [
        Binding("f2", "cart", "Cart"),
    ]

    def action_cart(self) -> None:
        if not self.app.world.profile_data.cart:
            self.notify("There are no operations in the cart! Cannot continue.", severity="warning")
            return
        self.app.push_screen(Cart())
