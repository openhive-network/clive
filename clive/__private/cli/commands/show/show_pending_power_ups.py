from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from helpy import wax as iwax
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
from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ShowPendingPowerUps(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
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
            votes_vests = Asset.Vests(amount=entry.val)
            hp_humanized = humanize_hive_power(
                iwax.calculate_vests_to_hp(
                    vests=votes_vests,
                    total_vesting_fund_hive=gdpo.total_vesting_fund_hive,
                    total_vesting_shares=gdpo.total_vesting_shares,
                )
            )
            vests_humanized = humanize_asset(votes_vests)
            hp_aligned, vests_aligned = align_to_dot(hp_humanized, vests_humanized, center_to=amount_title)
            delayed_votes_table.add_row(humanize_datetime(entry.time + delayed_voting_interval), hp_aligned)
            delayed_votes_table.add_row("", vests_aligned, end_section=True)

        console.print(delayed_votes_table)

    async def __get_delayed_voting_interval(self) -> timedelta:
        node_config = await self.world.node.cached.config
        return timedelta(seconds=node_config.HIVE_DELAYED_VOTING_TOTAL_INTERVAL_SECONDS)
