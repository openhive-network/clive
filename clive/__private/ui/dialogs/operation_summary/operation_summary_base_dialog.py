from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding

from clive.__private.core.constants.tui.bindings import (
    ADD_OPERATION_TO_CART_BINDING_KEY,
    FINALIZE_TRANSACTION_BINDING_KEY,
)
from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.buttons import CancelOneLineButton, ConfirmOneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


class OperationSummaryBaseDialog(ConfirmActionDialog, OperationActionBindings):
    """Base class for operation summary dialogs. Confirmation means that operation was added to cart or finalized."""

    BINDINGS = [
        Binding(ADD_OPERATION_TO_CART_BINDING_KEY, "dismiss_dialog_and_add_to_cart", "Add to cart"),
        Binding(FINALIZE_TRANSACTION_BINDING_KEY, "dismiss_dialog_and_finalize_transaction", "Finalize transaction"),
    ]

    CSS_PATH = [get_relative_css_path(__file__)]
    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES = False

    def create_buttons_content(self) -> ComposeResult:
        yield ConfirmOneLineButton(
            f"Add to cart ({ADD_OPERATION_TO_CART_BINDING_KEY.upper()})", id_="add-to-cart-button"
        )
        yield ConfirmOneLineButton(
            f"Finalize transaction ({FINALIZE_TRANSACTION_BINDING_KEY.upper()})", id_="finalize-button"
        )
        yield CancelOneLineButton()

    @on(ConfirmOneLineButton.Pressed, "#add-to-cart-button")
    async def action_dismiss_dialog_and_add_to_cart(self) -> None:
        super().action_add_to_cart()
        self.dismiss(result=True)

    @on(ConfirmOneLineButton.Pressed, "#finalize-button")
    async def action_dismiss_dialog_and_finalize_transaction(self) -> None:
        self.dismiss(result=True)
        await super().action_finalize_transaction()
