from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.storage.accounts import Account
from clive.models import Asset


@dataclass(kw_only=True)
class ShowBalances(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account = Account(name=self.account_name)

        (await self.world.commands.update_node_data(accounts=[account])).raise_if_error_occurred()

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

        console = Console()
        console.print(table)
