from dataclasses import dataclass

import typer
from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.profile_based_command import ProfileBasedCommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.commands.profile import ProfileList
from clive.__private.cli_error import CLIPrettyError
from clive.__private.storage.accounts import Account
from clive.models import Asset


@dataclass(kw_only=True)
class ListKeys(ProfileBasedCommand):
    async def run(self) -> None:
        profile_name = self.profile_data.name

        if not self.profile_data.is_working_account_set():
            raise CLIPrettyError(f"Working account is not set for `{profile_name}` profile.")

        public_keys = list(self.profile_data.working_account.keys)
        typer.echo(f"{profile_name}, your keys are:\n{public_keys}")


@dataclass(kw_only=True)
class ListNode(ProfileBasedCommand):
    async def run(self) -> None:
        typer.echo(self.profile_data.node_address)


@dataclass(kw_only=True)
class ListBalances(WorldBasedCommand):
    account_name: str

    async def run(self) -> None:
        account = Account(name=self.account_name)
        data = account.data

        (await self.world.commands.update_node_data(accounts=[account])).raise_if_error_occurred()

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


@dataclass(kw_only=True)
class ListProfiles(ProfileList):
    pass
