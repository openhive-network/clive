from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.logger import logger
from clive.exceptions import TransactionNotSignedError

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node
    from clive.models import Transaction


@dataclass(kw_only=True)
class Broadcast(Command):
    """Broadcasts the given operations/transactions to the blockchain."""

    node: Node
    transaction: Transaction

    async def _execute(self) -> None:
        if not self.transaction.is_signed():
            raise TransactionNotSignedError
        logger.info(f"Broadcasting transaction with id: {self.transaction.calculate_transaction_id()}")
        await self.node.api.network_broadcast.broadcast_transaction(trx=self.transaction)
