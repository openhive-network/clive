from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.visitors.operation.financial_operations_account_visitor import FinancialOperationsAccountCollector

if TYPE_CHECKING:
    from collections.abc import Iterable

    from clive.__private.core.accounts.accounts import KnownAccount


class PotentialKnownAccountCollector(FinancialOperationsAccountCollector):
    """Collects accounts that could potentially be known basing on the operations that are made to them."""

    def get_unknown_accounts(self, already_known_accounts: Iterable[KnownAccount]) -> list[str]:
        already_known_accounts_names = [account.name for account in already_known_accounts]
        return [account for account in self.accounts if account not in already_known_accounts_names]
