from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from rich.console import Console
from rich.table import Table
from rich.text import Text

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core import iwax
from clive.__private.core.formatters.humanize import (
    align_to_dot,
    humanize_asset,
    humanize_datetime,
    humanize_hive_power,
)


@dataclass(kw_only=True)
class ShowPendingPowerUps(WorldBasedCommand):
    """
    Show pending power ups for a given account.

    Args:
        account_name: The name of the account to show pending power ups for.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Show pending power ups for the specified account.

        This method retrieves the delayed votes for the account and displays them in a table format.
        The table includes the activation time and the amount of Hive Power (HP) that will be activated.
        If there are no pending power ups, a message is displayed indicating that there are none.

        Returns:
            None: This method does not return any value. It prints the results table directly to the console.
        """
        console = Console()
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        delayed_votes = accounts[0].delayed_votes

        if len(delayed_votes) == 0:
            message = (
                f"There are no pending power ups (delayed influence on governance) for account `{self.account_name}`."
            )
            console.print(colorize_content_not_available(message))
            return

        amount_title = "Amount"
        delayed_votes_table = Table(title=f"Current delayed votes for account `{self.account_name}`")
        delayed_votes_table.add_column(Text("Activation time", justify="center"), style="green", no_wrap=True)
        delayed_votes_table.add_column(Text(amount_title, justify="center"), style="green", no_wrap=True)

        gdpo = await self.world.node.cached.dynamic_global_properties
        delayed_voting_interval = await self.__get_delayed_voting_interval()

        for entry in delayed_votes:
            votes_vests = iwax.vests(entry.val)
            hp_humanized = humanize_hive_power(iwax.calculate_vests_to_hp(votes_vests, gdpo))
            vests_humanized = humanize_asset(votes_vests)
            hp_aligned, vests_aligned = align_to_dot(hp_humanized, vests_humanized, center_to=amount_title)
            delayed_votes_table.add_row(humanize_datetime(entry.time + delayed_voting_interval), hp_aligned)
            delayed_votes_table.add_row("", vests_aligned, end_section=True)

        console.print(delayed_votes_table)

    async def __get_delayed_voting_interval(self) -> timedelta:
        """
        Get the total interval for delayed voting from the node configuration.

        Returns:
            timedelta: The total interval for delayed voting.
        """
        node_config = await self.world.node.cached.config
        return timedelta(seconds=node_config.HIVE_DELAYED_VOTING_TOTAL_INTERVAL_SECONDS)
