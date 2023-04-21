from __future__ import annotations

from dataclasses import dataclass
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Final

from clive.__private.core.commands.command import Command
from clive.exceptions import CliveError

NODE_COMMUNICATION_ENABLED: Final[bool] = False

if NODE_COMMUNICATION_ENABLED:
    import httpx

    from clive.__private.core.mockcpp import serialize_transaction


if TYPE_CHECKING:
    from clive.__private.storage.mock_database import NodeAddress
    from clive.models.transaction import Transaction


class AlreadySerialized(str):
    pass


class PartiallySerializedEncoder(JSONEncoder):
    def encode(self, o: Any) -> str:
        if isinstance(o, AlreadySerialized):
            return o
        return super().encode(o)


@dataclass
class Broadcast(Command[None]):
    """Broadcasts the given operations/transactions to the blockchain."""

    class TransactionNotSignedError(CliveError):
        pass

    node_address: NodeAddress
    transaction: Transaction

    def execute(self) -> None:
        if not self.transaction.signed:
            raise self.TransactionNotSignedError()

        if NODE_COMMUNICATION_ENABLED:  # TODO: remove it when support for node communication will be granted
            httpx.post(
                str(self.node_address),
                json={
                    "id": 0,
                    "jsonrpc": "2.0",
                    "method": "network_broadcast_api.broadcast_transaction",
                    "params": {"trx": AlreadySerialized(serialize_transaction(self.transaction))},
                },
            )
            # TODO: some checks
