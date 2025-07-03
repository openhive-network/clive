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
    """
    Show authority of the account.

    Args:
        account_name: The name of the account whose authority is to be shown.
        authority: The type of authority to show (e.g., "active", "owner", "posting").
    """

    account_name: str
    authority: AuthorityType

    async def _run(self) -> None:
        """
        Show the authority of the specified account.

        Prints a table with the account or public key and its corresponding weight.

        Returns:
            None
        """
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
