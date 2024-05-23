from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.text import Text

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core.formatters.humanize import (
    align_to_dot,
    humanize_asset,
    humanize_datetime,
    humanize_hive_power,
)


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

        amount_title = "Amount"
        table = Table(title=f"Vesting delegation expirations for account `{self.account_name}`")
        table.add_column("Asset return date", justify="center", style="green", no_wrap=True)
        table.add_column(Text(amount_title, justify="center"), style="green", no_wrap=True)

        for delegation in delegations:
            hp = humanize_hive_power(delegation.amount.hp_balance)
            vests = humanize_asset(delegation.amount.vests_balance)
            hp_aligned, vests_aligned = align_to_dot(hp, vests, center_to=amount_title)
            table.add_row(humanize_datetime(delegation.expiration), hp_aligned)
            table.add_row("", vests_aligned, end_section=True)

        console.print(table)
