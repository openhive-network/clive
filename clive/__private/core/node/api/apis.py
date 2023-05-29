from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.node.api.account_history_api import AccountHistoryApi
from clive.__private.core.node.api.database_api import DatabaseApi
from clive.__private.core.node.api.network_broadcast_api import NetworkBroadcastApi

if TYPE_CHECKING:
    from clive.__private.core.node import Node


class Apis:
    def __init__(self, node: Node) -> None:
        self.network_broadcast = NetworkBroadcastApi(node)
        self.database_api = DatabaseApi(node)
        self.account_history_api = AccountHistoryApi(node)
