from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.formatters import humanize
from clive.__private.models.schemas import CancelTransferFromSavingsOperation
from clive.__private.ui.dialogs.operation_summary.operation_summary_base_dialog import OperationSummaryBaseDialog
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import SavingsWithdrawal


class CancelTransferFromSavingsDialog(OperationSummaryBaseDialog, OperationActionBindings):
    def __init__(self, transfer: SavingsWithdrawal) -> None:
        super().__init__("Cancel transfer from savings")
        self._transfer = transfer

    @property
    def from_account(self) -> str:
        return self.profile.accounts.working.name

    @property
    def realized_on(self) -> str:
        return humanize.humanize_datetime(self._transfer.complete)

    def create_dialog_content(self) -> ComposeResult:
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
