from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.logger import logger
from clive.dev import is_in_dev_mode

if TYPE_CHECKING:
    from clive.__private.models.schemas import (
        AccountUpdate2Operation,
        AccountWitnessProxyOperation,
        AccountWitnessVoteOperation,
        CancelTransferFromSavingsOperation,
        ClaimAccountOperation,
        CustomJsonOperation,
        DelegateVestingSharesOperation,
        OperationRepresentationUnion,
        OperationUnion,
        RecurrentTransferOperation,
        SetWithdrawVestingRouteOperation,
        TransferFromSavingsOperation,
        TransferOperation,
        TransferToSavingsOperation,
        TransferToVestingOperation,
        UpdateProposalVotesOperation,
        WithdrawVestingOperation,
    )


class OperationVisitor:
    def _default_visit(self, operation: OperationRepresentationUnion | OperationUnion) -> None:
        """Fallback if no specific method exists for an operation type."""
        if is_in_dev_mode():
            logger.debug(f"visitor not implemented for {operation.__class__.__name__}")  # type: ignore[union-attr]

    def visit(self, operation: OperationRepresentationUnion | OperationUnion) -> None:
        """Determine the correct method to call based on operation type."""
        method_name = f"visit_{operation.__class__.__name__.lower()}"  # type: ignore[union-attr]
        visit_method = getattr(self, method_name, self._default_visit)
        visit_method(operation)

    def visit_accountupdate2operation(self, operation: AccountUpdate2Operation) -> None:
        """Visitor for AccountUpdate2Operation operation."""
        self._default_visit(operation)

    def visit_accountwitnessproxyoperation(self, operation: AccountWitnessProxyOperation) -> None:
        """Visitor for AccountWitnessProxyOperation operation."""
        self._default_visit(operation)

    def visit_accountwitnessvoteoperation(self, operation: AccountWitnessVoteOperation) -> None:
        """Visitor for AccountWitnessVoteOperation operation."""
        self._default_visit(operation)

    def visit_canceltransferfromsavingsoperation(self, operation: CancelTransferFromSavingsOperation) -> None:
        """Visitor for CancelTransferFromSavingsOperation operation."""
        self._default_visit(operation)

    def visit_claimaccountoperation(self, operation: ClaimAccountOperation) -> None:
        """Visitor for ClaimAccountOperation operation."""
        self._default_visit(operation)

    def visit_customjsonoperation(self, operation: CustomJsonOperation) -> None:
        """Visitor for CustomJsonOperation operation."""
        self._default_visit(operation)

    def visit_delegatevestingsharesoperation(self, operation: DelegateVestingSharesOperation) -> None:
        """Visitor for DelegateVestingSharesOperation operation."""
        self._default_visit(operation)

    def visit_recurrenttransferoperation(self, operation: RecurrentTransferOperation) -> None:
        """Visitor for RecurrentTransferOperation operation."""
        self._default_visit(operation)

    def visit_setwithdrawvestingrouteoperation(self, operation: SetWithdrawVestingRouteOperation) -> None:
        """Visitor for SetWithdrawVestingRouteOperation operation."""
        self._default_visit(operation)

    def visit_transferfromsavingsoperation(self, operation: TransferFromSavingsOperation) -> None:
        """Visitor for TransferFromSavingsOperation operation."""
        self._default_visit(operation)

    def visit_transferoperation(self, operation: TransferOperation) -> None:
        """Visitor for TransferOperation operation."""
        self._default_visit(operation)

    def visit_transfertosavingsoperation(self, operation: TransferToSavingsOperation) -> None:
        """Visitor for TransferOperation operation."""
        self._default_visit(operation)

    def visit_transfertovestingoperation(self, operation: TransferToVestingOperation) -> None:
        """Visitor for TransferToVestingOperation operation."""
        self._default_visit(operation)

    def visit_updateproposalvotesoperation(self, operation: UpdateProposalVotesOperation) -> None:
        """Visitor for TransferToVestingOperation operation."""
        self._default_visit(operation)

    def visit_withdrawvestingoperation(self, operation: WithdrawVestingOperation) -> None:
        """Visitor for WithdrawVestingOperation operation."""
        self._default_visit(operation)
