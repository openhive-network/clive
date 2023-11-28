from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.models import Asset
from schemas.operations import TransferToSavingsOperation


@dataclass(kw_only=True)
class ProcessDeposit(OperationCommand):
    from_account: str
    to_account: str
    amount: str
    memo: str

    def _create_operation(self) -> TransferToSavingsOperation:
        return TransferToSavingsOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=Asset.from_legacy(self.amount.upper()),
            memo=self.memo,
        )
