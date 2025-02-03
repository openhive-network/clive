from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.buttons import (
    CancelOneLineButton,
    FinalizeTransactionOneLineButton,
)
from clive.__private.ui.widgets.buttons.add_to_cart_button import AddToCartOneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


class OperationSummaryBaseDialog(CliveActionDialog, OperationActionBindings, ABC):
    """Base class for operation summary dialogs. Confirmation means that operation was added to cart or finalized."""

    CSS_PATH = [get_relative_css_path(__file__)]
    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES = False

    def create_buttons_content(self) -> ComposeResult:
        yield AddToCartOneLineButton()
        yield FinalizeTransactionOneLineButton()
        yield CancelOneLineButton()

    async def action_add_to_cart(self) -> None:
        await super().action_add_to_cart()
        await self.confirm_dialog()

    async def action_finalize_transaction(self) -> None:
        await super().action_finalize_transaction()
        await self.confirm_dialog()

    @on(AddToCartOneLineButton.Pressed)
    async def _add_to_cart_with_button(self, event: AddToCartOneLineButton.Pressed) -> None:
        event.prevent_default()
        await self.action_add_to_cart()

    @on(FinalizeTransactionOneLineButton.Pressed)
    async def _finalize_transaction_with_button(self, event: FinalizeTransactionOneLineButton.Pressed) -> None:
        event.prevent_default()
        await self.action_finalize_transaction()
