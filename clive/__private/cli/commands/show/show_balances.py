from __future__ import annotations

from dataclasses import dataclass

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.models.asset import Asset
from clive.__private.si.core.show import ShowBalances as ShowBalancesSi


@dataclass(kw_only=True)
class ShowBalances(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        balances = await ShowBalancesSi(world=self.world, account_name=self.account_name).run()
        table = Table(title=f"Balances of `{self.account_name}` account")

        table.add_column("Type", justify="left", style="cyan", no_wrap=True)
        table.add_column("Amount", justify="right", style="green", no_wrap=True)
        table.add_row("HBD Liquid", f"{Asset.pretty_amount(balances.hbd_liquid)}")
        table.add_row("HBD Savings", f"{Asset.pretty_amount(balances.hbd_savings)}")
        table.add_row("HBD Unclaimed", f"{Asset.pretty_amount(balances.hbd_unclaimed)}")
        table.add_row("HIVE Liquid", f"{Asset.pretty_amount(balances.hive_liquid)}")
        table.add_row("HIVE Savings", f"{Asset.pretty_amount(balances.hive_savings)}")
        table.add_row("HIVE Unclaimed", f"{Asset.pretty_amount(balances.hive_unclaimed)}")

        print_cli(table)
