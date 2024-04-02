from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.models import Asset
from schemas.operations import TransferOperation


@dataclass(kw_only=True)
class Transfer(OperationCommand):
    from_account: str
    to: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operation(self) -> TransferOperation:
        return TransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
        )
