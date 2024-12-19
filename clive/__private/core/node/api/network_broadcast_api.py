from __future__ import annotations

from clive.__private.core.beekeeper.model import EmptyResponse  # noqa: TC001
from clive.__private.core.node.api.api import Api
from clive.__private.models import Transaction  # noqa: TC001


class NetworkBroadcastApi(Api):
    @Api.method
    async def broadcast_transaction(self, *, trx: Transaction) -> EmptyResponse:
        raise NotImplementedError
