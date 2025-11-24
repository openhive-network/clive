from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy.handle.remote import AppStatusProbeAsyncApiCollection

from clive.__private.core.node.async_hived.api.account_history_api import AsyncAccountHistoryApi
from clive.__private.core.node.async_hived.api.block_api import AsyncBlockApi
from clive.__private.core.node.async_hived.api.database_api import AsyncDatabaseApi
from clive.__private.core.node.async_hived.api.network_broadcast_api import AsyncNetworkBroadcastApi
from clive.__private.core.node.async_hived.api.rc_api import AsyncRcApi
from clive.__private.core.node.async_hived.api.reputation_api import AsyncReputationApi
from clive.__private.core.node.async_hived.api.transaction_status_api import (
    AsyncTransactionStatusApi,
)

if TYPE_CHECKING:
    from beekeepy.handle.remote import AsyncSendable


class HivedAsyncApiCollection(AppStatusProbeAsyncApiCollection):
    def __init__(self, owner: AsyncSendable) -> None:
        super().__init__(owner)
        self.account_history = AsyncAccountHistoryApi(owner=self._owner)
        self.block = AsyncBlockApi(owner=self._owner)
        self.database = AsyncDatabaseApi(owner=self._owner)
        self.network_broadcast = AsyncNetworkBroadcastApi(owner=self._owner)
        self.rc = AsyncRcApi(owner=self._owner)
        self.reputation = AsyncReputationApi(owner=self._owner)
        self.transaction_status = AsyncTransactionStatusApi(owner=self._owner)

        self.account_history_api = self.account_history
        self.block_api = self.block
        self.database_api = self.database
        self.network_broadcast_api = self.network_broadcast
        self.rc_api = self.rc
        self.reputation_api = self.reputation
        self.transaction_status_api = self.transaction_status
