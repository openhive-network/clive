from __future__ import annotations

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from clive.__private.models import schemas
from clive.__private.models.asset import Asset
from clive.__private.visitors.operation.financial_operations_account_collector import (
    FinancialOperationsAccountCollector,
)


class PotentialExchangeOperationsAccountCollector(FinancialOperationsAccountCollector):
    """Collects accounts with operations potentially problematic for exchanges (memoless, HBD, force-required)."""

    def __init__(self) -> None:
        super().__init__()
        self.memoless_transfers_accounts: set[str] = set()
        """Names of accounts with memoless transfers."""
        self.hbd_transfers_accounts: set[str] = set()
        """Names of accounts with hbd transfers."""

    def has_hbd_transfer_operations_to_account(self, account: str) -> bool:
        """Check if there are HBD transfer operations to the given account."""
        return account in self.hbd_transfers_accounts

    def has_memoless_transfer_operations_to_account(self, account: str) -> bool:
        """Check if there are memoless transfer operations to the given account."""
        return account in self.memoless_transfers_accounts

    def has_force_required_operations_to_account(self, account: str) -> bool:
        """
        Check if there are force required operations to the given account.

        Transfer is the only operation that is not considered a force-required operation for exchange.
        """
        return account in self.accounts

    @override
    def visit_transfer_operation(self, operation: schemas.TransferOperation) -> None:
        """
        Collect memoless and hbd transfers account names.

        Transfer to exchange should have asset in Hive and memo.

        If:
        1) the memo is empty string, it is considered a memoless transfer.
        2) the amount is Asset.Hbd, this is forbidden operation to exchange.
        """
        if operation.memo == "":
            self.memoless_transfers_accounts.add(operation.to)
            return
        if isinstance(operation.amount, Asset.Hbd):
            self.hbd_transfers_accounts.add(operation.to)
