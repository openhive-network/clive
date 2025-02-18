from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.constants.node import (
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
    VESTS_TO_REMOVE_DELEGATION,
)
from clive.__private.models import Asset
from clive.__private.visitors.operation.operation_visitor import OperationVisitor

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import (
        AccountName,
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

SCHEDULED_TRANSFER_REMOVE_VALUES: Final[list[Asset.Hive | Asset.Hbd]] = [
    Asset.hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
    Asset.hbd(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
]

DELEGATIONS_REMOVE_VALUES: Final[list[Asset.Hive | Asset.Hbd]] = [
    Asset.hive(VESTS_TO_REMOVE_DELEGATION),
    Asset.hbd(VESTS_TO_REMOVE_DELEGATION),
]


class UnknownAccountsCollector(OperationVisitor):
    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        self.unknown_accounts: set[AccountName] = set()

    def visit_account_witness_proxy_operation(self, operation: AccountWitnessProxyOperation) -> None:
        if operation.proxy and self.profile.accounts.is_account_unknown(operation.proxy):
            self.unknown_accounts.add(operation.proxy)  # type: ignore[arg-type]

    def visit_delegate_vesting_shares_operation(self, operation: DelegateVestingSharesOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.delegatee):
            self.unknown_accounts.add(operation.delegatee)

    def visit_recurrent_transfer_operation(self, operation: RecurrentTransferOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.to):
            self.unknown_accounts.add(operation.to)

    def visit_set_withdraw_vesting_route_operation(self, operation: SetWithdrawVestingRouteOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.to_account):
            self.unknown_accounts.add(operation.to_account)

    def visit_transfer_from_savings_operation(self, operation: TransferFromSavingsOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.to):
            self.unknown_accounts.add(operation.to)

    def visit_transfer_operation(self, operation: TransferOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.to):
            self.unknown_accounts.add(operation.to)

    def visit_transfer_to_savings_operation(self, operation: TransferToSavingsOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.to):
            self.unknown_accounts.add(operation.to)

    def visit_transfer_to_vesting_operation(self, operation: TransferToVestingOperation) -> None:
        if operation.to and self.profile.accounts.is_account_unknown(operation.to):
            self.unknown_accounts.add(operation.to)  # type: ignore[arg-type]

    def visit_cancel_transfer_from_savings_operation(self, operation: CancelTransferFromSavingsOperation) -> None:
        if self.profile.accounts.is_account_unknown(operation.from_):
            self.unknown_accounts.add(operation.from_)
