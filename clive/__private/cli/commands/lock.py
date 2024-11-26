from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.core.commands.lock_all import LockAll


@dataclass(kw_only=True)
class Lock(BeekeeperBasedCommand):
    async def validate(self) -> None:
        await self.validate_beekeeper_remote_address_set()
        await self.validate_beekeeper_session_token_set()
        await super().validate()

    async def _run(self) -> None:
        await LockAll(beekeeper=self.beekeeper).execute()
        typer.echo("All wallets have been locked.")
