from dataclasses import dataclass

import typer
from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core._async import asyncio_run
from clive.__private.storage.accounts import Account
from clive.models import Asset


@dataclass(kw_only=True)
class ListKeys(WorldBasedCommand):
    def run(self) -> None:
        profile_name = self.world.profile_data.name
        public_keys = list(self.world.profile_data.working_account.keys)

        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")


@dataclass(kw_only=True)
class ListNode(WorldBasedCommand):
    def run(self) -> None:
        typer.echo(self.world.node.address)


@dataclass(kw_only=True)
class ListBalances(WorldBasedCommand):
    account_name: str

    def run(self) -> None:
        account = Account(name=self.account_name)
        data = account.data

        asyncio_run(self.world.commands.update_node_data(accounts=[account])).raise_if_error_occurred()

        table = Table(title=f"Balances of `{self.account_name}` account")

        table.add_column("Type", justify="left", style="cyan", no_wrap=True)
        table.add_column("Amount", justify="right", style="green", no_wrap=True)

        table.add_row("HBD Liquid", f"{Asset.pretty_amount(data.hbd_balance)}")
        table.add_row("HBD Savings", f"{Asset.pretty_amount(data.hbd_savings)}")
        table.add_row("HBD Unclaimed", f"{Asset.pretty_amount(data.hbd_unclaimed)}")
        table.add_row("HIVE Liquid", f"{Asset.pretty_amount(data.hive_balance)}")
        table.add_row("HIVE Savings", f"{Asset.pretty_amount(data.hive_savings)}")
        table.add_row("HIVE Unclaimed", f"{Asset.pretty_amount(data.hive_unclaimed)}")

        console = Console()
        console.print(table)
