from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from clive.__private.logger import logger
from clive.__private.visitors.operation.operation_visitor import OperationVisitor

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import (
        AccountName,
        AccountWitnessProxyOperation,
        CancelTransferFromSavingsOperation,
        DelegateVestingSharesOperation,
        OperationUnion,
        RecurrentTransferOperation,
        SetWithdrawVestingRouteOperation,
        TransferFromSavingsOperation,
        TransferOperation,
        TransferToSavingsOperation,
        TransferToVestingOperation,
    )


class BadAccountsCollector(OperationVisitor):
    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        self.bad_accounts: set[AccountName] = set()

    @override
    def _default_visit(self, operation: OperationUnion) -> None:
        """We check only financial operations, for rest do nothing."""
        logger.debug(f"BadAccountsCollector has no visit function for `{operation.get_name_with_suffix()}`.")

    @override
    def visit_account_witness_proxy_operation(self, operation: AccountWitnessProxyOperation) -> None:
        if operation.proxy and self.profile.accounts.is_account_bad(operation.proxy):
            self.bad_accounts.add(operation.proxy)  # type: ignore[arg-type]

    @override
    def visit_delegate_vesting_shares_operation(self, operation: DelegateVestingSharesOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.delegatee):
            self.bad_accounts.add(operation.delegatee)

    @override
    def visit_recurrent_transfer_operation(self, operation: RecurrentTransferOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.to):
            self.bad_accounts.add(operation.to)

    @override
    def visit_set_withdraw_vesting_route_operation(self, operation: SetWithdrawVestingRouteOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.to_account):
            self.bad_accounts.add(operation.to_account)

    @override
    def visit_transfer_from_savings_operation(self, operation: TransferFromSavingsOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.to):
            self.bad_accounts.add(operation.to)

    @override
    def visit_transfer_operation(self, operation: TransferOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.to):
            self.bad_accounts.add(operation.to)

    @override
    def visit_transfer_to_savings_operation(self, operation: TransferToSavingsOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.to):
            self.bad_accounts.add(operation.to)

    @override
    def visit_transfer_to_vesting_operation(self, operation: TransferToVestingOperation) -> None:
        if operation.to and operation.to != operation.from_ and self.profile.accounts.is_account_bad(operation.to):
            self.bad_accounts.add(operation.to)  # type: ignore[arg-type]

    @override
    def visit_cancel_transfer_from_savings_operation(self, operation: CancelTransferFromSavingsOperation) -> None:
        if self.profile.accounts.is_account_bad(operation.from_):
            self.bad_accounts.add(operation.from_)
