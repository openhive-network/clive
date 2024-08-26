from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.models.aliased import AccountWitnessProxyOperation
from clive.__private.ui.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountWitnessProxy(OperationSummary):
    SECTION_TITLE: ClassVar[str] = "Account witness proxy"
    ADD_TO_CART_POP_SCREEN_MODE = "until_operations_or_dashboard"

    def __init__(self, *, new_proxy: str | None) -> None:
        super().__init__()
        self._new_proxy = new_proxy

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    @property
    def proxy_to_be_set(self) -> str:
        if self._new_proxy is None:
            return ""
        return self._new_proxy

    def content(self) -> ComposeResult:
        yield LabelizedInput("Account name", self.working_account_name)
        yield LabelizedInput("New proxy", self._new_proxy if self._new_proxy is not None else "Proxy will be removed")

    def _create_operation(self) -> AccountWitnessProxyOperation:
        return AccountWitnessProxyOperation(account=self.working_account_name, proxy=self.proxy_to_be_set)
