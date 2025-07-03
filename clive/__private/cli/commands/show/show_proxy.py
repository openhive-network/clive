from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available


@dataclass(kw_only=True)
class ShowProxy(WorldBasedCommand):
    """
    Show the proxy of an account.

    Args:
        account_name: The name of the account to show the proxy for.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Show the proxy of an account.

        This method retrieves the account's proxy and displays it in the console.
        If the account has no proxy set, it will print a message indicating that.

        Returns:
            None: The method prints the proxy information into the console.
        """
        console = Console()
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        proxy = accounts[0].proxy
        if not proxy:
            message = f"Account {self.account_name} has no proxy"
            console.print(colorize_content_not_available(message))
            return

        console.print(f"Account {self.account_name} has proxy set to {proxy}")
