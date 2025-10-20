from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferToSavingsOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessDeposit(OperationCommand):
    from_account: str
    to_account: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operations(self) -> ComposeTransaction:
        yield TransferToSavingsOperation(
            from_=self.from_account,
            to=self.to_account,
            amount=self.amount,
            memo=self.memo,
        )
