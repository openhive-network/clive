from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowNewAccountToken(WorldBasedCommand):
    """
    Show the number of new-account-tokens claimed by a specific account.

    Args:
        account_name: The name of the account to check for new-account-tokens.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Run the command to show the number of new-account-tokens claimed by the specified account.

        Returns:
            None: This method does not return any value, it prints the number of new-account-tokens to the console.
        """
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        pending_claimed_accounts = accounts[0].pending_claimed_accounts

        typer.echo(f"Number of new-account-tokens claimed by `{self.account_name}`: {pending_claimed_accounts}.")
