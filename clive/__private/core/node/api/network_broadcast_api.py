from __future__ import annotations

from clive.__private.core.beekeeper.model import EmptyResponse  # noqa: TCH001
from clive.__private.core.node.api.api import Api
from clive.models import Transaction  # noqa: TCH001


class NetworkBroadcastApi(Api):
    @Api.method
    async def broadcast_transaction(self, *, trx: Transaction) -> EmptyResponse:
        raise NotImplementedError
