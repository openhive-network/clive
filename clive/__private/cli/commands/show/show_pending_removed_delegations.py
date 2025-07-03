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
    """
    Show pending removed delegations for a given account.

    Args:
        account_name: The name of the account to show pending removed delegations for.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Show pending removed delegations for the specified account.

        This method retrieves the vesting delegation expirations for the account and displays them in a table format.
        The table includes the asset return date and the amount of Hive Power (HP) that will be returned.
        If there are no pending removed delegations, a message is displayed indicating that there are none.

        Returns:
            None: This method does not return any value. It prints the results table directly to the console.
        """
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
