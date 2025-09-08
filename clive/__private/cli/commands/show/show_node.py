from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class ShowNode(WorldBasedCommand):
    async def _run(self) -> None:
        print_cli(str(self.profile.node_address))
