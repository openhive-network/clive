from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import CancelTransferFromSavingsOperation


@dataclass(kw_only=True)
class ProcessWithdrawalCancel(OperationCommand):
    """
    Class to handle the cancellation of a withdrawal from savings.

    Args:
        from_account: The account from which the withdrawal is being canceled.
        request_id: The ID of the withdrawal request to be canceled.
    """

    from_account: str
    request_id: int

    async def _create_operation(self) -> CancelTransferFromSavingsOperation:
        """
        Create an instance with the provided details.

        Returns:
            CancelTransferFromSavingsOperation: An operation instance for canceling the withdrawal.
        """
        return CancelTransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
        )
