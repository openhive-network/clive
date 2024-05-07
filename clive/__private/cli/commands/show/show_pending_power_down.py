from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core.formatters.humanize import humanize_asset, humanize_datetime
from clive.models import Asset


@dataclass(kw_only=True)
class ShowPendingPowerDown(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        console = Console()
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        hp_data = wrapper.result_or_raise

        if hp_data.to_withdraw.vests_balance == Asset.vests(0):
            message = f"There is no pending power down operation for account `{self.account_name}`."
            console.print(colorize_content_not_available(message))
            return

        table = Table(title=f"Pending power down for account `{self.account_name}`")
        table.add_column("Next power down", justify="right", style="green", no_wrap=True)
        table.add_column("Amount [HP]", justify="right", style="green", no_wrap=True)
        table.add_column("Amount [VESTS]", justify="right", style="green", no_wrap=True)
        table.add_row(
            humanize_datetime(hp_data.next_vesting_withdrawal),
            humanize_asset(hp_data.next_power_down.hp_balance, show_symbol=False),
            humanize_asset(hp_data.next_power_down.vests_balance, show_symbol=False),
        )
        console.print(table)
