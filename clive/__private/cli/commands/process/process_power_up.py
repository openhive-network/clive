from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferToVestingOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessPowerUp(OperationCommand):
    from_account: str
    to_account: str
    amount: Asset.Hive

    async def _create_operations(self) -> ComposeTransaction:
        yield TransferToVestingOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=self.amount,
        )
