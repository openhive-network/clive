from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.node.api.network_broadcast_api import NetworkBroadcastApi

if TYPE_CHECKING:
    from clive.__private.core.node import Node


class Apis:
    def __init__(self, node: Node) -> None:
        self.network_broadcast = NetworkBroadcastApi(node)
