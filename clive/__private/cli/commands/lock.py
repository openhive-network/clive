from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.core.commands.lock import Lock as CoreLock


@dataclass(kw_only=True)
class Lock(BeekeeperBasedCommand):
    async def _run(self) -> None:
        await CoreLock(session=await self.beekeeper.session).execute()
        typer.echo("All wallets have been locked.")
