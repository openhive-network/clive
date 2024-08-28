from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.types import AuthorityType

if TYPE_CHECKING:
    from clive.__private.core.authority import Authority


@dataclass(kw_only=True)
class ShowAuthority(WorldBasedCommand):
    account_name: str
    authority: AuthorityType

    async def _run(self) -> None:
        account = TrackedAccount(name=self.account_name)
        (await self.world.commands.update_authority_data(account=account)).raise_if_error_occurred()
        authorities = account.authorities

        console = Console()

        authority_struct: Authority = getattr(authorities, self.authority)
        title = (
            f"{self.authority} authority of `{self.account_name}` account, weight threshold is"
            f" {authority_struct.weight_threshold}:"
        )

        table = Table(title=title)
        table.add_column("account or public key", min_width=53)
        table.add_column("weight", justify="right")
        for auth, weight in [*authority_struct.key_auths, *authority_struct.account_auths]:
            table.add_row(f"{auth}", f"{weight}")

        console.print(table)
