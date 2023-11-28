from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from schemas.operations import CancelTransferFromSavingsOperation


@dataclass(kw_only=True)
class ProcessCancelWithdrawal(OperationCommand):
    from_account: str
    request_id: str

    def _create_operation(self) -> CancelTransferFromSavingsOperation:
        return CancelTransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
        )
