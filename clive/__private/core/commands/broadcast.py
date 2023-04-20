from __future__ import annotations
from json import JSONEncoder, dumps
from typing import Any

import httpx
from clive.__private.core.beekeeper.handle import BeekeeperRemote
from clive.__private.core.beekeeper.url import Url
from clive.__private.core.commands.command import Command
from clive.__private.core.mockcpp import serialize_transaction
from clive.__private.storage.mock_database import NodeAddress
from clive.exceptions import CliveError
from clive.models.operation import Operation
from clive.models.transaction import Transaction


class AlreadySerialized(str):
    pass


class PartiallySerializedEncoder(JSONEncoder):
    def encode(self, o: Any) -> str:
        if isinstance(o, AlreadySerialized):
            return o
        return super().encode(o)


class Broadcast(Command[None]):
    """Broadcasts the given operations/transactions to the blockchain."""

    class TransactionNotSignedError(CliveError):
        pass

    def __init__(self, *, address: NodeAddress, transaction: Transaction) -> None:
        super().__init__(result_default=None)
        self.__transaction = transaction
        self.__address = address

    def execute(self) -> None:
        if not self.__transaction.signed:
            raise self.TransactionNotSignedError()
        httpx.post(
            str(self.__address),
            json={
                "id": 0,
                "jsonrpc": "2.0",
                "method": "network_broadcast_api.broadcast_transaction",
                "params": {"trx": AlreadySerialized(serialize_transaction(self.__transaction))},
            },
        )
        # TODO: some checks
