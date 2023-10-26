from __future__ import annotations

from clive.__private.core.node.api.api import Api
from schemas.apis import transaction_status_api  # noqa: TCH001


class TransactionStatusApi(Api):
    @Api.method
    async def find_transaction(self, transaction_id: str) -> transaction_status_api.FindTransaction:
        raise NotImplementedError
