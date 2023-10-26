from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.node.api.account_history_api import AccountHistoryApi
from clive.__private.core.node.api.database_api import DatabaseApi
from clive.__private.core.node.api.network_broadcast_api import NetworkBroadcastApi
from clive.__private.core.node.api.rc_api import RcApi
from clive.__private.core.node.api.reputation_api import ReputationApi
from clive.__private.core.node.api.transaction_status_api import TransactionStatusApi

if TYPE_CHECKING:
    from clive.__private.core.node.node import BaseNode


class Apis:
    def __init__(self, node: BaseNode) -> None:
        self.network_broadcast = NetworkBroadcastApi(node)
        self.database_api = DatabaseApi(node)
        self.account_history_api = AccountHistoryApi(node)
        self.reputation_api = ReputationApi(node)
        self.rc_api = RcApi(node)
        self.transaction_status_api = TransactionStatusApi(node)
