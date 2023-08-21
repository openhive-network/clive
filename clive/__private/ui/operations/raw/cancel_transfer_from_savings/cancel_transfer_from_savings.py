from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual._on import on
from textual.containers import Grid, ScrollableContainer
from textual.widgets import Pretty, Static

from clive.__private.core.get_default_from_model import get_default_from_model
from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.id_input import IdInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset
    from schemas.database_api.fundaments_of_reponses import SavingsWithdrawalsFundament


class Body(Grid):
    """Content that includes from and request_id parameter. In savings tab also parameters of transfer."""


class FromSavingsTransferParameters(Grid):
    """Content that includes data about transfer from savings when cancelling it by button."""


class PlaceTaker(Static):
    """Use to ensure proper display of the grid."""


class CancelTransferFromSavings(RawOperationBaseScreen):
    def __init__(self, cancelling_transfer: SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd] | None = None) -> None:
        if cancelling_transfer:
            self.__request_id = cancelling_transfer.request_id
            self.__to_account = cancelling_transfer.to
            self.__amount = cancelling_transfer.amount
            self.__memo = cancelling_transfer.memo
            self.__realized_on = datetime.strftime(cancelling_transfer.complete, "%Y-%m-%dT%H:%M:%S")
        self.__cancelling_transfer = cancelling_transfer
        super().__init__()

        if self.__cancelling_transfer is None:
            default_request_id = str(get_default_from_model(CancelTransferFromSavingsOperation, "request_id", int))
            self.__request_id_input = IdInput(label="request id", value=default_request_id)
        else:
            self.__request_id_input = IdInput(label="request id", value=self.__request_id)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Cancel transfer from savings")
            with ScrollableContainer(), Body():
                yield InputLabel("from")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, classes="parameters-label")
                if self.__cancelling_transfer is None:
                    yield from self.__request_id_input.compose()
                    yield PlaceTaker()
                    yield Static("Data of the searched transfer:", id="transfer-searching-label")
                    yield PlaceTaker()
                    yield Pretty("No transfer with the specified request_id")
                else:
                    yield InputLabel("request id")
                    yield EllipsedStatic(str(self.__request_id), classes="parameters-label")
                if self.__cancelling_transfer is not None:
                    with FromSavingsTransferParameters():
                        yield Static("to-account", id="to-column")
                        yield Static("realized-on (UTC)", id="realized-column")
                        yield Static("amount", id="amount-column")
                        yield Static("memo", id="memo-column")
                        yield Static(self.__to_account, classes="transfer-parameters")
                        yield Static(self.__realized_on, classes="transfer-parameters")
                        yield Static(Asset.to_legacy(self.__amount), classes="transfer-parameters")
                        yield Static(self.__memo, classes="transfer-parameters")

    @on(IdInput.Changed)
    def find_typed_id(self, event: IdInput.Changed) -> None:
        pending_transfers: list[SavingsWithdrawalsFundament[Asset.Hive, Asset.Hbd]] = (
            self.app.world.node.api.database_api.find_savings_withdrawals(
                account=self.app.world.profile_data.working_account.name
            ).withdrawals
        )
        transfer_pretty: Pretty = self.query_one(Pretty)
        for transfer in pending_transfers:
            if str(transfer.request_id) == event.value:
                transfer_pretty.update(
                    {
                        "to": transfer.to,
                        "amount": Asset.to_legacy(transfer.amount),
                        "realized_on": datetime.strftime(transfer.complete, "%Y-%m-%dT%H:%M:%S"),
                    }
                )
                break
            transfer_pretty.update("No transfer with the specified request_id")

    def _create_operation(self) -> CancelTransferFromSavingsOperation:
        request_id = self.__request_id_input.value
        if not request_id:
            return None

        return CancelTransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
        )
