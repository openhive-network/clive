from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand


@dataclass(kw_only=True)
class CliveLock(BeekeeperBasedCommand):
    async def _run(self) -> None:
        await self.beekeeper.api.lock_all()
        typer.echo("All wallets have been locked.")
