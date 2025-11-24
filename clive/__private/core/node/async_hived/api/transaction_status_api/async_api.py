from __future__ import annotations

from datetime import datetime  # noqa: TC003

from beekeepy.handle.remote import AbstractAsyncApi

from schemas.apis import transaction_status_api


class TransactionStatusApi(AbstractAsyncApi):
    @AbstractAsyncApi.endpoint_jsonrpc
    async def find_transaction(
        self, *, transaction_id: str, expiration: datetime | None = None
    ) -> transaction_status_api.FindTransaction:
        raise NotImplementedError
