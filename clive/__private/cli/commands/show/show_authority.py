from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand

if TYPE_CHECKING:
    from clive.__private.cli.types import AuthorityType


@dataclass(kw_only=True)
class ShowAuthority(WorldBasedCommand):
    account_name: str
    authority: AuthorityType

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        console = Console()

        title = (
            f"{self.authority} authority of `{account.name}` account, weight threshold is"
            f" {account[self.authority].weight_threshold}:"
        )

        table = Table(title=title)
        table.add_column("account or public key", min_width=53)
        table.add_column("weight", justify="right")
        for auth, weight in [*account[self.authority].key_auths, *account[self.authority].account_auths]:
            table.add_row(f"{auth}", f"{weight}")

        console.print(table)
