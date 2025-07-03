from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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
from clive.__private.models import Asset

if TYPE_CHECKING:
    from clive.__private.models import HpVestsBalance


@dataclass(kw_only=True)
class ShowPendingPowerDown(WorldBasedCommand):
    """
    Show pending power down for the specified account.

    Args:
        account_name: The name of the account to show pending power down for.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Run the command to show pending power down for the specified account.

        This method retrieves the pending power down data for the account and displays it in a formatted table.
        The table includes the next withdrawal date, the next withdrawal amount, total to be withdrawn,
        amount withdrawn, and the remaining amount to withdraw.
        If there is no pending power down operation, a message is displayed indicating that.

        Returns:
            None: This method does not return any value. It prints the results table directly to the console.
        """
        console = Console()
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        hp_data = wrapper.result_or_raise

        if hp_data.to_withdraw.vests_balance == Asset.vests(0):
            message = f"There is no pending power down operation for account `{self.account_name}`."
            console.print(colorize_content_not_available(message))
            return

        def humanize_align_shares_balance(balance: HpVestsBalance, center_to: str) -> tuple[str, str]:
            """
            Humanizes and aligns the shares balance for display in the table.

            Args:
                balance: The balance to humanize and align.
                center_to: The string to center the alignment to.

            Returns:
                tuple: A tuple containing the humanized and aligned Hive Power and Vests balances.
            """
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
        console.print(table)
