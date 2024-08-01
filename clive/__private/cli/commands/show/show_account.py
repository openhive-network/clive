from dataclasses import dataclass, field

from rich.console import Console
from rich.padding import Padding
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.alarms.alarms_storage import AlarmsStorage
from clive.__private.core.formatters.humanize import (
    humanize_asset,
    humanize_datetime,
    humanize_percent,
    humanize_timedelta,
)
from clive.__private.storage.accounts import TrackedAccount
from clive.__private.storage.mock_database import NodeData
from clive.models.asset import Asset


@dataclass(kw_only=True)
class ShowAccount(WorldBasedCommand):
    account_name: str
    account_data: NodeData = field(init=False)
    account_alarms: AlarmsStorage = field(init=False)

    async def _run(self) -> None:
        console = Console()
        account = TrackedAccount(name=self.account_name)

        (await self.world.commands.find_accounts(accounts=[self.account_name])).raise_if_error_occurred()

        try:
            (await self.world.commands.update_node_data(accounts=[account])).raise_if_error_occurred()
            (await self.world.commands.update_alarms_data(accounts=[account])).raise_if_error_occurred()
        except AssertionError:
            console.print(f"Could not get data for account {self.account_name}")
            return

        self.account_data = account.data
        self.account_alarms = account.alarms

        table_general_information = self.__create_table_general_information()
        table_the_balances = self.__create_table_the_balances()
        table_the_voting = self.__create_table_the_voting()
        console.print(table_general_information)
        console.print(Padding(""))
        console.print(table_the_balances)
        console.print(Padding(""))
        console.print(table_the_voting)

    def __get_account_type_name(self) -> str | None:
        if self.world.profile_data.is_account_working(self.account_name):
            return "Working account"
        if self.world.profile_data.is_account_watched(self.account_name):
            return "Watched account"
        if self.world.profile_data.is_account_tracked(self.account_name):
            return "Tracked account"
        return None

    def __create_table_general_information(self) -> Table:
        general_information = Table(title="General information", show_header=False)
        general_information.add_column("", justify="left", style="cyan", no_wrap=True)
        general_information.add_column("", justify="right", style="green", no_wrap=True)

        account_type = self.__get_account_type_name()

        general_information.add_row("Account name", self.account_name)
        if account_type:
            general_information.add_row("Account type", account_type)
        general_information.add_row("Last history entry", humanize_datetime(self.account_data.last_history_entry))
        general_information.add_row("Account update", humanize_datetime(self.account_data.last_account_update))
        general_information.add_row("Number of new account token", str(self.account_data.pending_claimed_accounts))
        general_information.add_row("Number of alarms", str(len(self.account_alarms.all_alarms)))

        return general_information

    def __create_table_the_balances(self) -> Table:
        the_balances = Table(title="The balances", show_header=False)
        hive_symbol = Asset.get_symbol(Asset.Hive)
        hbd_symbol = Asset.get_symbol(Asset.Hbd)
        vests_symbol = Asset.get_symbol(Asset.Vests)
        the_balances.add_column("", justify="left", style="cyan", no_wrap=True)
        the_balances.add_column("", justify="right", style="green", no_wrap=True)
        the_balances.add_column("", justify="right", style="green", no_wrap=True)
        the_balances.add_column("", justify="right", style="green", no_wrap=True)

        pretty_amount = Asset.pretty_amount

        the_balances.add_section()
        the_balances.add_row("", hbd_symbol, hive_symbol, vests_symbol)
        the_balances.add_section()
        the_balances.add_row(
            "Liquid",
            pretty_amount(self.account_data.hbd_balance),
            pretty_amount(self.account_data.hive_balance),
            pretty_amount(Asset.vests(self.account_data.hp_balance)),
        )
        the_balances.add_row(
            "Savings",
            pretty_amount(self.account_data.hbd_savings),
            pretty_amount(self.account_data.hive_savings),
            pretty_amount(self.account_data.hp_unclaimed),
        )
        return the_balances

    def __create_table_the_voting(self) -> Table:
        the_voting = Table(title="The voting", show_header=False)
        the_voting.add_column("", justify="left", style="cyan", no_wrap=True)
        the_voting.add_column("", justify="right", style="green", no_wrap=True)
        the_voting.add_column("", justify="right", style="green", no_wrap=True)
        the_voting.add_column("", justify="right", style="green", no_wrap=True)

        rc = self.account_data.rc_manabar_ensure
        vote = self.account_data.vote_manabar
        downvote = self.account_data.downvote_manabar

        full_regain_message = "How much time to be full again"
        the_voting.add_row("", "RC", "Voting", "Downvoting")
        the_voting.add_section()
        the_voting.add_row(
            "Percent",
            humanize_percent(rc.percentage),
            humanize_percent(vote.percentage),
            humanize_percent(downvote.percentage),
        )
        the_voting.add_row(
            "Current mana",
            humanize_asset(rc.value),
            humanize_asset(vote.value),
            humanize_asset(downvote.value),
        )
        the_voting.add_row(
            full_regain_message,
            humanize_timedelta(rc.full_regeneration),
            humanize_timedelta(vote.full_regeneration),
            humanize_timedelta(downvote.full_regeneration),
        )
        return the_voting
