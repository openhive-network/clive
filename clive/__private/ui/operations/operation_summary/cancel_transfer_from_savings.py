from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

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

    def content(self) -> ComposeResult:
        yield LabelizedInput("From", self.app.world.profile_data.working_account.name)
        yield LabelizedInput("Request id", str(self._transfer.request_id))

    def _create_operation(self) -> CancelTransferFromSavingsOperation:
        request_id = self._transfer.request_id

        return CancelTransferFromSavingsOperation(
            from_=self.app.world.profile_data.working_account.name,
            request_id=request_id,
        )
