from __future__ import annotations

from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand


@dataclass(kw_only=True)
class ShowMemoKey(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        typer.echo(f"memo key of {account.name} account: {account.memo_key}")
