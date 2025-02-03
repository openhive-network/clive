from __future__ import annotations

from clive.__private.core.constants.tui.bindings import ADD_OPERATION_TO_CART_BINDING_KEY
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class AddToCartButton(CliveButton):
    DEFAULT_CSS = """
        AddToCartButton {
            width: 25;
        }
        """

    class Pressed(CliveButton.Pressed):
        """Message send when AddToCartButton is pressed."""

    def __init__(self) -> None:
        super().__init__(
            f"Add to cart ({ADD_OPERATION_TO_CART_BINDING_KEY.upper()})", id_="add-to-cart-button", variant="success"
        )


class AddToCartOneLineButton(OneLineButton, AddToCartButton):
    class Pressed(AddToCartButton.Pressed):
        """Message sent when AddToCartOneLineButton is pressed."""
