from __future__ import annotations

from typing import TYPE_CHECKING, override

from clive.__private.core.constants.node import (
    EMPTY_MEMO_VALUE,
    PERCENT_TO_REMOVE_WITHDRAW_ROUTE,
)
from clive.__private.core.constants.node_special_assets import (
    DELEGATION_REMOVE_ASSETS,
    SCHEDULED_TRANSFER_REMOVE_ASSETS,
)

if TYPE_CHECKING:
    from clive.__private.models import schemas
from clive.__private.visitors.operation.operation_visitor import OperationVisitor


class MemolessTransferAndForceableOperationsCollector(OperationVisitor):
    """Collects accounts names with memoless transfers and forceable operations."""

    def __init__(self) -> None:
        self.memoless_transfers_accounts: set[str] = set()
        """Names of accounts with memoless transfers."""
        self.forceable_operations_accounts: set[str] = set()
        """Names of accounts with forceable operations."""

    def has_memoless_transfers_to_account(self, account: str) -> bool:
        """Check if there are memoless transfers to the given account."""
        return account in self.memoless_transfers_accounts

    def has_forceable_operations_to_account(self, account: str) -> bool:
        """Check if there are forceable operations to the given account."""
        return account in self.forceable_operations_accounts

    # Memoless
    @override
    def visit_transfer_operation(self, operation: schemas.TransferOperation) -> None:
        if operation.memo is EMPTY_MEMO_VALUE:
            self.memoless_transfers_accounts.add(operation.to)

    # Forceable
    @override
    def visit_transfer_from_savings_operation(self, operation: schemas.TransferFromSavingsOperation) -> None:
        self.forceable_operations_accounts.add(operation.to)

    @override
    def visit_recurrent_transfer_operation(self, operation: schemas.RecurrentTransferOperation) -> None:
        if operation.amount not in SCHEDULED_TRANSFER_REMOVE_ASSETS:
            self.forceable_operations_accounts.add(operation.to)

    @override
    def visit_transfer_to_savings_operation(self, operation: schemas.TransferToSavingsOperation) -> None:
        self.forceable_operations_accounts.add(operation.to)

    @override
    def visit_delegate_vesting_shares_operation(self, operation: schemas.DelegateVestingSharesOperation) -> None:
        if operation.vesting_shares not in DELEGATION_REMOVE_ASSETS:
            self.forceable_operations_accounts.add(operation.delegatee)

    @override
    def visit_transfer_to_vesting_operation(self, operation: schemas.TransferToVestingOperation) -> None:
        self.forceable_operations_accounts.add(operation.to)

    @override
    def visit_set_withdraw_vesting_route_operation(self, operation: schemas.SetWithdrawVestingRouteOperation) -> None:
        if operation.percent != PERCENT_TO_REMOVE_WITHDRAW_ROUTE:
            self.forceable_operations_accounts.add(operation.to_account)
