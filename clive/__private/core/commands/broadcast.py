from __future__ import annotations

from dataclasses import dataclass
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, Final

from clive.__private.core.beekeeper.model import JSONRPCRequest
from clive.__private.core.commands.command import Command
from clive.exceptions import CliveError

NODE_COMMUNICATION_ENABLED: Final[bool] = False

if NODE_COMMUNICATION_ENABLED:
    import httpx

    from clive.__private.core.iwax import serialize_transaction


if TYPE_CHECKING:
    from clive.core.url import Url
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

    node_address: Url
    transaction: Transaction

    def execute(self) -> None:
        if not self.transaction.signed:
            raise self.TransactionNotSignedError()

        if NODE_COMMUNICATION_ENABLED:  # TODO: remove it when support for node communication will be granted
            httpx.post(
                self.node_address.as_string(),
                json=JSONRPCRequest(
                    method="network_broadcast_api.broadcast_transaction",
                    params={"trx": AlreadySerialized(serialize_transaction(self.transaction))},
                ).dict(by_alias=True),
            )
            # TODO: some checks
