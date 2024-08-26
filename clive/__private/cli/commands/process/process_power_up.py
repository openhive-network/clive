from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.aliased import TransferToVestingOperation

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessPowerUp(OperationCommand):
    from_account: str
    to_account: str
    amount: Asset.Hive

    async def _create_operation(self) -> TransferToVestingOperation:
        return TransferToVestingOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=self.amount,
        )
