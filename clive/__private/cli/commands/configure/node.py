from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.url import Url


@dataclass(kw_only=True)
class SetNode(WorldBasedCommand):
    node_address: str

    async def _run(self) -> None:
        url = Url.parse(self.node_address)
        self.profile._set_node_address(url)
