from __future__ import annotations

from beekeepy.handle.remote import AbstractAsyncApi

from hiveio_api import network_broadcast_api
from hiveio_api.operations import Transaction


class NetworkBroadcastApi(AbstractAsyncApi):
    @AbstractAsyncApi.endpoint_jsonrpc
    async def broadcast_transaction(self, *, trx: Transaction) -> network_broadcast_api.BroadcastTransactionResponse:
        raise NotImplementedError
