from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.models import Asset
from schemas.operations import TransferOperation


@dataclass(kw_only=True)
class Transfer(OperationCommand):
    to: str
    amount: str
    memo: str

    async def _create_operation(self) -> TransferOperation:
        return TransferOperation(
            from_=self.world.profile_data.working_account.name,
            to=self.to,
            amount=Asset.from_legacy(self.amount.upper()),
            memo=self.memo,
        )
