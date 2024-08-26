from __future__ import annotations

from clive.__private.core.node.api.api import Api
from clive.__private.models.aliased import TransactionStatus  # noqa: TCH001


class TransactionStatusApi(Api):
    @Api.method
    async def find_transaction(self, *, transaction_id: str) -> TransactionStatus:
        raise NotImplementedError
