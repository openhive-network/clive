from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.exceptions import TransactionNotSignedError

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.models import Transaction


@dataclass(kw_only=True)
class Broadcast(Command):
    """
    Broadcasts the given transaction to the blockchain.

    Attributes:
        node: The node to which the transaction will be broadcasted.
        transaction: The transaction to be broadcasted.
    """

    node: Node
    transaction: Transaction

    async def _execute(self) -> None:
        if not self.transaction.is_signed:
            raise TransactionNotSignedError
        await self.node.api.network_broadcast.broadcast_transaction(trx=self.transaction)
