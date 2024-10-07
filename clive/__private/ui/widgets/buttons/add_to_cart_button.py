from __future__ import annotations

from clive.__private.ui.widgets.buttons.clive_button import CliveButton


class AddToCartButton(CliveButton):
    DEFAULT_CSS = """
        AddToCartButton {
            width: 25;
        }
        """

    class Pressed(CliveButton.Pressed):
        """Message send when AddToCartButton is pressed."""

    def __init__(self) -> None:
        super().__init__("Add to cart (F2)", id_="add-to-cart-button", variant="success")
