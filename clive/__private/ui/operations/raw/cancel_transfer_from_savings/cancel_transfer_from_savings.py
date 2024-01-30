from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.text_input import TextInput
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.aliased import SavingsWithdrawals


class Body(Grid):
    """All the content of the screen, excluding the title."""


class CancelTransferFromSavings(RawOperationBaseScreen):
    CSS_PATH = [
        *RawOperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def __init__(self, transfer: SavingsWithdrawals) -> None:
        super().__init__()
        self._transfer = transfer

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Cancel transfer")
        with ScrollableContainer(), Body():
            yield TextInput(
                "From",
                value=self.app.world.profile_data.working_account.name,
                always_show_title=True,
                required=False,
                disabled=True,
            )
            yield TextInput(
                "Request id",
                value=str(self._transfer.request_id),
                always_show_title=True,
                required=False,
                disabled=True,
            )

    def action_add_to_cart(self) -> None:
        if self.create_operation() in self.app.world.profile_data.cart:
            self.notify("Operation already in the cart", severity="error")
        else:
            super().action_add_to_cart()

    def _create_operation(self) -> CancelTransferFromSavingsOperation:
        request_id = self._transfer.request_id

        return CancelTransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
        )
