from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.models import Asset
from schemas.operations import TransferToVestingOperation


@dataclass(kw_only=True)
class ProcessPowerUp(OperationCommand):
    from_account: str
    to_account: str
    amount: str

    async def _create_operation(self) -> TransferToVestingOperation:
        return TransferToVestingOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=Asset.from_legacy(self.amount.upper()),
        )
