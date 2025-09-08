from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class ShowNewAccountToken(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        pending_claimed_accounts = accounts[0].pending_claimed_accounts

        print_cli(f"Number of new-account-tokens claimed by `{self.account_name}`: {pending_claimed_accounts}.")
