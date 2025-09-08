from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table
from rich.text import Text

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.formatters.humanize import (
    align_to_dot,
    humanize_asset,
    humanize_datetime,
    humanize_hive_power,
)
from clive.__private.models import Asset

if TYPE_CHECKING:
    from clive.__private.models import HpVestsBalance


@dataclass(kw_only=True)
class ShowPendingPowerDown(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        hp_data = wrapper.result_or_raise

        if hp_data.to_withdraw.vests_balance == Asset.vests(0):
            print_content_not_available(f"There is no pending power down operation for account `{self.account_name}`.")
            return

        def humanize_align_shares_balance(balance: HpVestsBalance, center_to: str) -> tuple[str, str]:
            hp = humanize_hive_power(balance.hp_balance)
            vests = humanize_asset(balance.vests_balance)
            hp_aligned, vests_aligned = align_to_dot(hp, vests, center_to=center_to)
            return hp_aligned, vests_aligned

        title_amount = "Next withdrawal amount"
        title_total = "Total to be withdrawn"
        title_withdrawn = "Withdrawn"
        title_remains = "Remains to withdraw"
        hp_amount, vests_amount = humanize_align_shares_balance(hp_data.next_power_down, center_to=title_amount)
        hp_total, vests_total = humanize_align_shares_balance(hp_data.to_withdraw, center_to=title_total)
        hp_withdrawn, vests_withdrawn = humanize_align_shares_balance(hp_data.withdrawn, center_to=title_withdrawn)
        hp_remains, vests_remains = humanize_align_shares_balance(hp_data.remaining, center_to=title_remains)

        table = Table(title=f"Pending power down for account `{self.account_name}`")
        table.add_column(Text("Next withdrawal date", justify="center"), style="green", no_wrap=True)
        table.add_column(Text(title_amount, justify="center"), style="green", no_wrap=True)
        table.add_column(Text(title_total, justify="center"), style="green", no_wrap=True)
        table.add_column(Text(title_withdrawn, justify="center"), style="green", no_wrap=True)
        table.add_column(Text(title_remains, justify="center"), style="green", no_wrap=True)
        table.add_row(humanize_datetime(hp_data.next_vesting_withdrawal), hp_amount, hp_total, hp_withdrawn, hp_remains)
        table.add_row("", vests_amount, vests_total, vests_withdrawn, vests_remains)
        print_cli(table)
