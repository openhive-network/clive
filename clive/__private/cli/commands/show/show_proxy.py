from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowProxy(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        if self.world.profile_data.working_account.name == self.account_name:
            proxy = self.world.profile_data.working_account.data.proxy
        else:
            core_account = await self.world.node.api.database_api.find_accounts(accounts=[self.account_name])
            proxy = core_account.proxy

        if not proxy:
            typer.echo(f"Account {self.account_name} has no proxy")
            return

        typer.echo(f"Account {self.account_name} has proxy set to {proxy}")
