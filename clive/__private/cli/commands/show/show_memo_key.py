from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class ShowMemoKey(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        print_cli(f"memo key of {account.name} account: {account.memo_key}")
