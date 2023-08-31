from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual.containers import Grid, ScrollableContainer
from textual.widgets import Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.models import Asset
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament


class CancelTransferParameters(Grid):
    """Content that includes from and request_id parameter - cancel transfer from savings parameters."""


class FromSavingsTransferParameters(Grid):
    """Content that includes data about transfer from savings when cancelling it by button."""


class CancelTransferFromSavings(RawOperationBaseScreen):
    def __init__(self, transfer: SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]) -> None:
        super().__init__()
        self.__transfer = transfer

    def create_left_panel(self) -> ComposeResult:
        yield BigTitle("Cancel transfer")
        with ScrollableContainer():
            with CancelTransferParameters():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, classes="parameters-label")
                yield InputLabel("request id")
                yield EllipsedStatic(str(self.__transfer.request_id), classes="parameters-label")
            with FromSavingsTransferParameters():
                yield Static("to-account", id="to-column")
                yield Static("realized-on (UTC)", id="realized-column")
                yield Static("amount", id="amount-column")
                yield Static("memo", id="memo-column")
                yield Static(self.__transfer.to, classes="transfer-parameters")
                yield Static(self.__realized_on, classes="transfer-parameters")
                yield Static(Asset.to_legacy(self.__transfer.amount), classes="transfer-parameters")
                yield Static(self.__transfer.memo, classes="transfer-parameters")
            yield Static()

    def _create_operation(self) -> CancelTransferFromSavingsOperation | None:
        request_id = self.__transfer.request_id
        return CancelTransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
        )

    @property
    def __realized_on(self) -> str:
        return datetime.strftime(self.__transfer.complete, "%Y-%m-%dT%H:%M:%S")
