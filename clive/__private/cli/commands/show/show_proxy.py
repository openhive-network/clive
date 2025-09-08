from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available


@dataclass(kw_only=True)
class ShowProxy(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        proxy = accounts[0].proxy
        if not proxy:
            print_content_not_available(f"Account {self.account_name} has no proxy")
            return

        print_cli(f"Account {self.account_name} has proxy set to {proxy}")
