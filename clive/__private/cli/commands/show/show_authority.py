from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.si.core.show import ShowAuthority as ShowAuthoritySi

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular


@dataclass(kw_only=True)
class ShowAuthority(WorldBasedCommand):
    account_name: str
    authority: AuthorityLevelRegular

    async def _run(self) -> None:
        authority_info, authorities = await ShowAuthoritySi(self.world, self.account_name, self.authority).run()

        title = (
            f"{authority_info.authority_type} authority of `{authority_info.authority_owner_account_name}` account,"
            f"\nweight threshold is {authority_info.weight_threshold}:"
        )

        table = Table(title=title)
        table.add_column("account or public key", min_width=53)
        table.add_column("weight", justify="right")
        for authority in authorities:
            table.add_row(f"{authority.account_or_public_key}", f"{authority.weight}")

        print_cli(table)
