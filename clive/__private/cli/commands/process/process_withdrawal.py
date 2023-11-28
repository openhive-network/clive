from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.models import Asset
from schemas.operations import TransferFromSavingsOperation


@dataclass(kw_only=True)
class ProcessWithdrawal(OperationCommand):
    from_account: str
    request_id: str
    to_account: str
    amount: str
    memo: str

    def _create_operation(self) -> TransferFromSavingsOperation:
        return TransferFromSavingsOperation(
            from_=self.from_account,
            request_id=self.request_id,
            to=self.to_account,
            amount=Asset.from_legacy(self.amount.upper()),
            memo=self.memo,
        )
