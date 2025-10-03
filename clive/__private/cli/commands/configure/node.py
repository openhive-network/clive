from __future__ import annotations

from dataclasses import dataclass

import beekeepy.interfaces as bki

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class SetNode(WorldBasedCommand):
    node_address: str

    async def _run(self) -> None:
        url = bki.HttpUrl(self.node_address)
        self.profile._set_node_address(url)
