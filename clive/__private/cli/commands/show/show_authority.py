from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular


@dataclass(kw_only=True)
class ShowAuthority(WorldBasedCommand):
    account_name: str
    authority: AuthorityLevelRegular

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        title = (
            f"{self.authority} authority of `{account.name}` account,"
            f"\nweight threshold is {account[self.authority].weight_threshold}:"
        )

        table = Table(title=title)
        table.add_column("account or public key", min_width=53)
        table.add_column("weight", justify="right")
        for auth, weight in [*account[self.authority].key_auths, *account[self.authority].account_auths]:
            table.add_row(f"{auth}", f"{weight}")

        print_cli(table)
