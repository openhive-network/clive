from __future__ import annotations

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from clive.__private.models import schemas
from clive.__private.models.asset import Asset
from clive.__private.visitors.operation.financial_operations_account_collector import (
    FinancialOperationsAccountCollector,
)


class PotentialExchangeOperationsAccountCollector(FinancialOperationsAccountCollector):
    """
    Collects exchange accounts with potentially problematic operations to them.

    Can be used to check if memoless/HBD transfer was detected and
    if there is any other unsafe operations (other than transfer).
    """

    def __init__(self) -> None:
        super().__init__()
        self.memoless_transfers_accounts: set[str] = set()
        """Names of accounts with memoless transfers."""
        self.hbd_transfers_accounts: set[str] = set()
        """Names of accounts with hbd transfers."""

    def has_hbd_transfer_operations_to_exchange(self, account: str) -> bool:
        """
        Check if there are HBD transfer operations to the given exchange account.

        Args:
            account: The exchange account name to check for HBD transfers.

        Returns:
            True if there are HBD transfer operations to the account, False otherwise.
        """
        return account in self.hbd_transfers_accounts

    def has_memoless_transfer_operations_to_exchange(self, account: str) -> bool:
        """
        Check if there are memoless transfer operations to the given exchange account.

        Args:
            account: The exchange account name to check for memoless transfers.

        Returns:
            True if there are memoless transfer operations to the account, False otherwise.
        """
        return account in self.memoless_transfers_accounts

    def has_unsafe_operation_to_exchange(self, account: str) -> bool:
        """
        Check if there are unsafe operations to the given exchange account.

        Notice:
            Transfer is the only operation considered a safe operation to the exchange account.

        Args:
            account: The exchange account name to check for unsafe operations.

        Returns:
            True if there are unsafe operations to the account, False otherwise.
        """
        return account in self.accounts

    @override
    def visit_transfer_operation(self, operation: schemas.TransferOperation) -> None:
        """
        Collect memoless and hbd transfers account names.

        Notice:
            Transfer to exchange should have asset in Hive and memo.

            - If the memo is empty string, it is considered a memoless transfer.
            - If the amount is Asset.Hbd, this is forbidden operation to exchange.

        Args:
            operation: The transfer operation to process.
        """
        if operation.memo == "":
            self.memoless_transfers_accounts.add(operation.to)
            return
        if operation.amount.nai() == Asset.Hbd.nai():
            self.hbd_transfers_accounts.add(operation.to)
