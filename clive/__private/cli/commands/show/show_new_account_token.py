from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowNewAccountToken(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        pending_claimed_accounts = accounts[0].pending_claimed_accounts

        typer.echo(f"Number of new-account-tokens claimed by `{self.account_name}`: {pending_claimed_accounts}.")
