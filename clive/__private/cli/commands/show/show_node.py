from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand


@dataclass(kw_only=True)
class ShowNode(ProfileBasedCommand):
    async def _run(self) -> None:
        typer.echo(self.profile.node_address)
