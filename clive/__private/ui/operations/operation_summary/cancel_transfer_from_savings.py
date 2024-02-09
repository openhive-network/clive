from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.formatters import humanize
from clive.__private.ui.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from schemas.operations import CancelTransferFromSavingsOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.aliased import SavingsWithdrawals


class CancelTransferFromSavings(OperationSummary):
    BIG_TITLE: ClassVar[str] = "Cancel transfer"

    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES: ClassVar[bool] = False

    def __init__(self, transfer: SavingsWithdrawals) -> None:
        super().__init__()
        self._transfer = transfer

    @property
    def from_account(self) -> str:
        return self.app.world.profile_data.working_account.name

    @property
    def realized_on(self) -> str:
        return humanize.humanize_datetime(self._transfer.complete)

    def content(self) -> ComposeResult:
        yield LabelizedInput("Request id", str(self._transfer.request_id))
        yield LabelizedInput("Realized on", self.realized_on)
        yield LabelizedInput("From", self.from_account)
        yield LabelizedInput("To", self._transfer.to)
        yield LabelizedInput("Amount", self._transfer.amount.as_legacy())
        yield LabelizedInput("Memo", self._transfer.memo)

    def _create_operation(self) -> CancelTransferFromSavingsOperation:
        request_id = self._transfer.request_id

        return CancelTransferFromSavingsOperation(
            from_=self.from_account,
            request_id=request_id,
        )
