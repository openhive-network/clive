from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.memo_command import MemoCommand
from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.models.schemas import TransferOperation

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class Transfer(OperationCommand, MemoCommand):
    from_account: str
    to: str
    amount: Asset.LiquidT

    async def _create_operations(self) -> ComposeTransaction:
        memo = await self._maybe_encrypt_memo(self.ensure_memo, self.from_account, self.to)
        yield TransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=memo,
        )
