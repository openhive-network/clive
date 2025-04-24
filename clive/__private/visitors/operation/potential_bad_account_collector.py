from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.visitors.operation.financial_operations_account_collector import (
    FinancialOperationsAccountCollector,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


class PotentialBadAccountCollector(FinancialOperationsAccountCollector):
    """Collects accounts that could potentially be bad basing on the operations that are made to them."""

    def get_bad_accounts(self, bad_accounts: Iterable[str]) -> list[str]:
        return [account for account in self.accounts if account in bad_accounts]
