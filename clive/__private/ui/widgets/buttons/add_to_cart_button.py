from __future__ import annotations

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class AddToCartButton(OneLineButton):
    DEFAULT_CSS = """
        AddToCartButton {
            width: 25;
        }
        """

    class Pressed(OneLineButton.Pressed):
        """Message send when AddToCartButton is pressed."""

    def __init__(self) -> None:
        super().__init__("Add to cart (F2)", id_="add-to-cart-button", variant="success")
