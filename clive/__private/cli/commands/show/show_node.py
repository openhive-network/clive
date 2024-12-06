from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowNode(WorldBasedCommand):
    async def _run(self) -> None:
        typer.echo(self.profile.node_address)
