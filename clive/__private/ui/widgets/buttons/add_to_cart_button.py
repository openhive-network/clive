from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.bindings import ADD_TO_CART_BINDING_KEY
from clive.__private.ui.widgets.buttons.binding_button import BindingButton
from clive.__private.ui.widgets.buttons.clive_button import CliveButton

if TYPE_CHECKING:
    from textual.binding import Binding


class AddToCartButton(BindingButton):
    DEFAULT_CSS = """
        AddToCartButton {
            width: 25;
        }
        """

    class Pressed(CliveButton.Pressed):
        """Message send when AddToCartButton is pressed."""

    def __init__(self, bindings_list: list[Binding]) -> None:
        super().__init__(ADD_TO_CART_BINDING_KEY, bindings_list)
