from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import typer
from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import InvalidAssetError
from clive.__private.core import iwax
from clive.__private.core.formatters.humanize import humanize_asset, humanize_datetime
from clive.models import Asset


@dataclass(kw_only=True)
class ShowPendingPowerUps(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        delayed_votes = accounts[0].delayed_votes

        if len(delayed_votes) == 0:
            typer.echo(
                f"There are no pending power ups (delayed influence on governance) for account `{self.account_name}`."
            )
            return

        console = Console()
        delayed_votes_table = Table(title=f"Current delayed votes for account `{self.account_name}`")
        delayed_votes_table.add_column("Activation time", justify="right", style="green", no_wrap=True)
        delayed_votes_table.add_column("Amount in HP", justify="right", style="green", no_wrap=True)
        delayed_votes_table.add_column("Amount in VESTS", justify="right", style="green", no_wrap=True)

        gdpo = await self.world.app_state.get_dynamic_global_properties()
        delayed_voting_interval = await self.__get_delayed_voting_interval_from_api()

        for entry in delayed_votes:
            votes_vests = iwax.vests(entry.val)
            if not isinstance(votes_vests, Asset.Vests):
                raise InvalidAssetError(votes_vests, Asset.Vests)
            delayed_votes_table.add_row(
                humanize_datetime(entry.time + delayed_voting_interval),
                humanize_asset(iwax.calculate_vests_to_hp(votes_vests, gdpo), show_symbol=False),
                humanize_asset(votes_vests, show_symbol=False),
            )

        console.print(delayed_votes_table)

    async def __get_delayed_voting_interval_from_api(self) -> timedelta:
        node_config = await self.world.node.api.database_api.get_config()
        return timedelta(seconds=node_config.HIVE_DELAYED_VOTING_TOTAL_INTERVAL_SECONDS)
