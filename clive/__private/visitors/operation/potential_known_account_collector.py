from __future__ import annotations

from typing import TYPE_CHECKING, override

from clive.__private.core.constants.node import CANCEL_PROXY_VALUE
from clive.__private.visitors.operation.financial_operations_account_collector import (
    FinancialOperationsAccountCollector,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clive.__private.core.accounts.accounts import KnownAccount
    from clive.__private.models import schemas


class PotentialKnownAccountCollector(FinancialOperationsAccountCollector):
    """Collects accounts that could potentially be known basing on the operations that are made to them."""

    def get_unknown_accounts(self, already_known_accounts: Iterable[KnownAccount]) -> list[str]:
        already_known_accounts_names = [account.name for account in already_known_accounts]
        return [account for account in self.accounts if account not in already_known_accounts_names]

    @override
    def visit_account_witness_proxy_operation(self, operation: schemas.AccountWitnessProxyOperation) -> None:
        if operation.proxy != CANCEL_PROXY_VALUE:
            self.accounts.add(operation.proxy)

    @override
    def visit_change_recovery_account_operation(self, operation: schemas.ChangeRecoveryAccountOperation) -> None:
        self.accounts.add(operation.new_recovery_account)
