from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowProxy(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        proxy = accounts[0].proxy
        if not proxy:
            typer.echo(f"Account {self.account_name} has no proxy")
            return

        typer.echo(f"Account {self.account_name} has proxy set to {proxy}")
