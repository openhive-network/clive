from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowNode(WorldBasedCommand):
    """Show the node address of the current profile."""

    async def _run(self) -> None:
        """
        Show the node address of the current profile.

        Returns:
            None: This method does not return anything, it prints the node address in console.
        """
        typer.echo(self.profile.node_address)
