from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core.formatters.humanize import humanize_asset, humanize_datetime


@dataclass(kw_only=True)
class ShowPendingRemovedDelegations(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        console = Console()
        delegations = (
            await self.world.commands.find_vesting_delegation_expirations(account=self.account_name)
        ).result_or_raise

        if len(delegations) == 0:
            message = f"There are no removed delegations for account `{self.account_name}`."
            console.print(colorize_content_not_available(message))
            return

        table = Table(title=f"Vesting delegation expirations for account `{self.account_name}`")
        table.add_column("id", justify="left", style="cyan", no_wrap=True)
        table.add_column("vesting shares", justify="right", style="green", no_wrap=True)
        table.add_column("expiration", justify="right", style="green", no_wrap=True)

        for delegation in delegations:
            table.add_row(
                f"{delegation.id_}",
                humanize_asset(delegation.vesting_shares),
                humanize_datetime(delegation.expiration),
            )

        console.print(table)
