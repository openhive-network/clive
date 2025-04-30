from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferToVestingOperation

if TYPE_CHECKING:
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessPowerUp(OperationCommand):
    from_account: str
    to_account: str
    amount: Asset.Hive
    force: bool

    async def is_forceable(self) -> bool:
        return True

    def is_force_enabled(self) -> bool:
        return self.force

    async def _create_operation(self) -> TransferToVestingOperation:
        return TransferToVestingOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=self.amount,
        )
