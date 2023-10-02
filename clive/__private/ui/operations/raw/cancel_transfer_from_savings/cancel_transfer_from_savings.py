from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Grid, ScrollableContainer
from textual.css.query import NoMatches
from textual.widgets import Input, Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.operations.savings_operations.savings_data import SavingsDataProvider
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.models import Asset
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.aliased import SavingsWithdrawals


class CancelTransferParameters(Grid):
    """Content that includes from and request_id - parameters of cancel transfer from savings operation."""


class FromSavingsTransferParameters(Grid):
    """Content containing data cancelling transfers from savings when canceled via a button or searched through input."""

    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, transfer: SavingsWithdrawals) -> None:
        super().__init__()
        self.__transfer = transfer

    def compose(self) -> ComposeResult:
        yield Static("to-account", id="to-column")
        yield Static("realized-on (UTC)", id="realized-column")
        yield Static("amount", id="amount-column")
        yield Static("memo", id="memo-column")
        yield Static(self.__transfer.to, classes="transfer-parameters")
        yield Static(self.__realized_on, classes="transfer-parameters")  # type: ignore[arg-type]
        yield Static(Asset.to_legacy(self.__transfer.amount), classes="transfer-parameters")
        yield Static(self.__transfer.memo, classes="transfer-parameters")

    @property
    def __realized_on(self) -> str | None:
        if self.__transfer:
            return datetime.strftime(self.__transfer.complete, "%Y-%m-%dT%H:%M:%S")
        return None


class CancelTransferFromSavings(RawOperationBaseScreen):
    def __init__(self, transfer: SavingsWithdrawals | None = None) -> None:
        super().__init__()
        self.__transfer = transfer
        self.__scrollable_container = ScrollableContainer()
        self.__provider: SavingsDataProvider | None = None
        self.__id_input = IdInput(
            "request id",
            id_="id-input",
            disabled=self.is_transfer_given,
            value=transfer.request_id if self.is_transfer_given else None,  # type: ignore[union-attr]
        )

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Cancel transfer")
        with self.__scrollable_container:
            with CancelTransferParameters():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
                yield from self.__id_input.compose()
                if not self.is_transfer_given:
                    with SavingsDataProvider() as provider:
                        self.__provider = provider
            if self.is_transfer_given:
                yield FromSavingsTransferParameters(self.__transfer)  # type: ignore[arg-type]

    @property
    def is_transfer_given(self) -> bool:
        return self.__transfer is not None

    @on(Input.Changed)
    def search_given_transfer(self, event: Input.Changed) -> None:
        if self.__provider is None:
            return
        if self.__provider.content.pending_transfers:
            for transfer in self.__provider.content.pending_transfers:
                if event.value == str(transfer.request_id):
                    self.replace_displayed_transfer(transfer)
                    return
        self.replace_displayed_transfer()

    def replace_displayed_transfer(self, transfer: SavingsWithdrawals | None = None) -> None:
        try:
            self.query_one(FromSavingsTransferParameters).remove()
        except NoMatches:
            pass
        finally:
            if transfer is not None:
                new_transfer_container = FromSavingsTransferParameters(transfer)
                self.__scrollable_container.mount(new_transfer_container)

    def action_add_to_cart(self) -> None:
        if self.create_operation() in self.app.world.profile_data.cart:
            self.notify("Operation already in the cart", severity="error")
        else:
            super().action_add_to_cart()

    def _create_operation(self) -> CancelTransferFromSavingsOperation | None:
        request_id = self.__transfer.request_id if self.__transfer else self.__id_input.value
        return CancelTransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
        )
