from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.core.commands.lock_all import LockAll


@dataclass(kw_only=True)
class Lock(BeekeeperBasedCommand):
    async def _run(self) -> None:
        await LockAll(beekeeper=self.beekeeper).execute()
        typer.echo("All wallets have been locked.")
