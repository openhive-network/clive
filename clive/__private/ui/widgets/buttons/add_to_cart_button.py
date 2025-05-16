from __future__ import annotations

from clive.__private.core.constants.tui.operations_common_bindings import ADD_OPERATION_TO_CART
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
        super().__init__(
            f"Add to cart ({self.app.bound_key_short(ADD_OPERATION_TO_CART.id)})",
            id_="add-to-cart-button",
            variant="success",
        )
