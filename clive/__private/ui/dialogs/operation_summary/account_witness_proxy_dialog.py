from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.models.schemas import AccountWitnessProxyOperation
from clive.__private.ui.dialogs.operation_summary.operation_summary_base_dialog import OperationSummaryBaseDialog
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import Account


class AccountWitnessProxyDialog(OperationSummaryBaseDialog):
    def __init__(self, *, new_proxy: str | None) -> None:
        super().__init__("Account witness proxy")
        self._new_proxy = new_proxy

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    @property
    def proxy_to_be_set(self) -> str:
        if self._new_proxy is None:
            return ""
        return self._new_proxy

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("Account name", self.working_account_name)
        yield LabelizedInput("New proxy", self._new_proxy if self._new_proxy is not None else "Proxy will be removed")

    def get_account_to_be_marked_as_known(self) -> str | Account | None:
        return self._new_proxy

    def _close_when_cancelled(self) -> None:
        self.dismiss(result=False)

    def _close_when_confirmed(self) -> None:
        self.dismiss(result=True)

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(account=self.working_account_name, proxy=self.proxy_to_be_set)
