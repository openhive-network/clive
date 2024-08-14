from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.widgets.clive_widget import CliveWidget


class CartBinding(CliveWidget):
    BINDINGS = [
        Binding("f2", "cart", "Cart"),
    ]

    def action_cart(self) -> None:
        if not self.profile.cart:
            self.notify("There are no operations in the cart! Cannot continue.", severity="warning")
            return
        self.app.push_screen(Cart())
