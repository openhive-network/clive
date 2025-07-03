from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowMemoKey(WorldBasedCommand):
    """
    Show the memo key of a specified account.

    Args:
        account_name: The name of the account whose memo key is to be displayed.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Run the command to show the memo key of the specified account.

        Returns:
            None: This method does not return any value, it prints the memo key to the console.
        """
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        typer.echo(f"memo key of {account.name} account: {account.memo_key}")
