from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.operations.transfer_operations import create_transfer_operation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class Transfer(OperationCommand):
    from_account: str
    to: str
    amount: Asset.LiquidT
    memo: str

    async def _create_operations(self) -> ComposeTransaction:
        yield create_transfer_operation(
            from_account=self.from_account,
            to_account=self.to,
            amount=self.amount,
            memo=self.memo,
        )
