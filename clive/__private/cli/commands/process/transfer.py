from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferOperation

if TYPE_CHECKING:
    from clive.__private.models import Asset


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
