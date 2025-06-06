from __future__ import annotations

from typing import TYPE_CHECKING, override

from clive.__private.core.constants.node import CANCEL_PROXY_VALUE
from clive.__private.visitors.operation.financial_operations_account_collector import (
    FinancialOperationsAccountCollector,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clive.__private.models import schemas


class PotentialBadAccountCollector(FinancialOperationsAccountCollector):
    """Collects accounts that could potentially be bad basing on the operations that are made to them."""

    def get_bad_accounts(self, bad_accounts: Iterable[str]) -> list[str]:
        return [account for account in self.accounts if account in bad_accounts]

    @override
    def visit_account_witness_proxy_operation(self, operation: schemas.AccountWitnessProxyOperation) -> None:
        if operation.proxy != CANCEL_PROXY_VALUE:
            self.accounts.add(operation.proxy)
