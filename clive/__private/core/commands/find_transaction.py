from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.models.schemas import TransactionStatus

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class FindTransaction(CommandWithResult[TransactionStatus]):
    node: Node
    transaction_id: str

    async def _execute(self) -> None:
        self._result = await self.node.api.transaction_status_api.find_transaction(transaction_id=self.transaction_id)
