from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import CancelTransferFromSavingsOperation


@dataclass(kw_only=True)
class ProcessWithdrawalCancel(OperationCommand):
    from_account: str
    request_id: int

    async def _create_operation(self) -> CancelTransferFromSavingsOperation:
        return CancelTransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
        )
