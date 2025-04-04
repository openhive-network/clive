from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available


@dataclass(kw_only=True)
class ShowProxy(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        console = Console()
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        proxy = accounts[0].proxy
        if not proxy:
            message = f"Account {self.account_name} has no proxy"
            console.print(colorize_content_not_available(message))
            return

        console.print(f"Account {self.account_name} has proxy set to {proxy}")
