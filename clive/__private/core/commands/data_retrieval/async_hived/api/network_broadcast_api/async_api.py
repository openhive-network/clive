from __future__ import annotations

from beekeepy.handle.remote import AbstractAsyncApi

from schemas.apis import network_broadcast_api
from schemas.transaction import Transaction


class NetworkBroadcastApi(AbstractAsyncApi):
    @AbstractAsyncApi.endpoint_jsonrpc
    async def broadcast_transaction(self, *, trx: Transaction) -> network_broadcast_api.BroadcastTransaction:
        raise NotImplementedError
