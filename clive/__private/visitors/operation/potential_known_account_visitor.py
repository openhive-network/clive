from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from typing_extensions import override

from clive.__private.core.constants.node import PERCENT_TO_REMOVE_WITHDRAW_ROUTE
from clive.__private.core.constants.node_special_assets import (
    DELEGATIONS_REMOVE_ASSETS,
    SCHEDULED_TRANSFER_REMOVE_ASSETS,
)
from clive.__private.visitors.operation.operation_visitor import OperationVisitor

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import KnownAccount
    from clive.__private.models.schemas import (
        AccountWitnessProxyOperation,
        CancelTransferFromSavingsOperation,
        DelegateVestingSharesOperation,
        RecurrentTransferOperation,
        SetWithdrawVestingRouteOperation,
        TransferFromSavingsOperation,
        TransferOperation,
        TransferToSavingsOperation,
        TransferToVestingOperation,
    )


class PotentialKnownAccountCollector(OperationVisitor):
    """Collects accounts that could potentially be known basing on the operations that are made to them."""

    def __init__(self) -> None:
        self.accounts: set[str] = set()
        """Names of accounts that could potentially be known."""

    def get_unknown_accounts(self, already_known_accounts: Iterable[KnownAccount]) -> list[str]:
        already_known_accounts_names = [account.name for account in already_known_accounts]
        return [account for account in self.accounts if account not in already_known_accounts_names]

    @override
    def visit_account_witness_proxy_operation(self, operation: AccountWitnessProxyOperation) -> None:
        if operation.proxy:
            self.accounts.add(operation.proxy)

    @override
    def visit_delegate_vesting_shares_operation(self, operation: DelegateVestingSharesOperation) -> None:
        if operation.vesting_shares not in DELEGATIONS_REMOVE_ASSETS:
            self.accounts.add(operation.delegatee)

    @override
    def visit_recurrent_transfer_operation(self, operation: RecurrentTransferOperation) -> None:
        if operation.amount not in SCHEDULED_TRANSFER_REMOVE_ASSETS:
            self.accounts.add(operation.to)

    @override
    def visit_set_withdraw_vesting_route_operation(self, operation: SetWithdrawVestingRouteOperation) -> None:
        if operation.percent != PERCENT_TO_REMOVE_WITHDRAW_ROUTE:
            self.accounts.add(operation.to_account)

    @override
    def visit_transfer_from_savings_operation(self, operation: TransferFromSavingsOperation) -> None:
        self.accounts.add(operation.to)

    @override
    def visit_transfer_operation(self, operation: TransferOperation) -> None:
        self.accounts.add(operation.to)

    @override
    def visit_transfer_to_savings_operation(self, operation: TransferToSavingsOperation) -> None:
        self.accounts.add(operation.to)

    @override
    def visit_transfer_to_vesting_operation(self, operation: TransferToVestingOperation) -> None:
        if operation.to:
            self.accounts.add(operation.to)

    @override
    def visit_cancel_transfer_from_savings_operation(self, operation: CancelTransferFromSavingsOperation) -> None:
        self.accounts.add(operation.from_)
