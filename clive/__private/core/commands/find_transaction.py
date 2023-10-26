from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node


@dataclass(kw_only=True)
class FindTransaction(CommandWithResult[str]):
    node: Node
    transaction_id: str

    async def _execute(self) -> None:
        status = await self.node.api.transaction_status_api.find_transaction(transaction_id=self.transaction_id)
        self._result = str(status)
