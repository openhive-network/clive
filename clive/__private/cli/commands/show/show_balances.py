from __future__ import annotations

from dataclasses import dataclass

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ShowBalances(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account = TrackedAccount(name=self.account_name)

        await self.world.commands.update_node_data(accounts=[account])

        table = Table(title=f"Balances of `{self.account_name}` account")

        table.add_column("Type", justify="left", style="cyan", no_wrap=True)
        table.add_column("Amount", justify="right", style="green", no_wrap=True)
        data = account.data
        table.add_row("HBD Liquid", f"{Asset.pretty_amount(data.hbd_balance)}")
        table.add_row("HBD Savings", f"{Asset.pretty_amount(data.hbd_savings)}")
        table.add_row("HBD Unclaimed", f"{Asset.pretty_amount(data.hbd_unclaimed)}")
        table.add_row("HIVE Liquid", f"{Asset.pretty_amount(data.hive_balance)}")
        table.add_row("HIVE Savings", f"{Asset.pretty_amount(data.hive_savings)}")
        table.add_row("HIVE Unclaimed", f"{Asset.pretty_amount(data.hive_unclaimed)}")
        table.add_row("HP Owned", f"{Asset.pretty_amount(data.owned_hp_balance.hp_balance)}")
        table.add_row("HP Unclaimed", f"{Asset.pretty_amount(data.unclaimed_hp_balance.hp_balance)}")

        print_cli(table)
