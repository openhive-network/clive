from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.constants.node import (
    PERCENT_TO_REMOVE_WITHDRAW_ROUTE,
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
    VESTS_TO_REMOVE_DELEGATION,
)
from clive.__private.models import Asset
from clive.__private.models.schemas import AccountName
from clive.__private.visitors.operation.operation_visitor import OperationVisitor

if TYPE_CHECKING:
    from clive.__private.models.schemas import (
        AccountWitnessProxyOperation,
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


class KnownAccountsVisitor(OperationVisitor):
    def __init__(self) -> None:
        self.known_accounts: set[AccountName] = set()

    def visit_accountwitnessproxyoperation(self, operation: AccountWitnessProxyOperation) -> None:
        if isinstance(operation.proxy, AccountName):
            self.known_accounts.add(operation.proxy)

    def visit_delegatevestingsharesoperation(self, operation: DelegateVestingSharesOperation) -> None:
        if operation.vesting_shares not in DELEGATIONS_REMOVE_VALUES:
            self.known_accounts.add(operation.delegatee)

    def visit_recurrenttransferoperation(self, operation: RecurrentTransferOperation) -> None:
        if operation.amount not in SCHEDULED_TRANSFER_REMOVE_VALUES:
            self.known_accounts.add(operation.to)

    def visit_setwithdrawvestingrouteoperation(self, operation: SetWithdrawVestingRouteOperation) -> None:
        if operation.percent != PERCENT_TO_REMOVE_WITHDRAW_ROUTE:
            self.known_accounts.add(operation.to_account)

    def visit_transferfromsavingsoperation(self, operation: TransferFromSavingsOperation) -> None:
        self.known_accounts.add(operation.to)

    def visit_transferoperation(self, operation: TransferOperation) -> None:
        self.known_accounts.add(operation.to)

    def visit_transfertosavingsoperation(self, operation: TransferToSavingsOperation) -> None:
        self.known_accounts.add(operation.to)

    def visit_transfertovestingoperation(self, operation: TransferToVestingOperation) -> None:
        if isinstance(operation.to, AccountName):
            self.known_accounts.add(operation.to)
