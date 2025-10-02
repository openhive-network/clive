from __future__ import annotations

from dataclasses import dataclass, field
from functools import partial
from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.console import Group
from rich.padding import Padding
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.formatters.humanize import (
    humanize_asset,
    humanize_datetime,
    humanize_hive_power_with_comma,
    humanize_manabar_regeneration_time,
    humanize_percent,
)
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.alarms.alarms_storage import AlarmsStorage
    from clive.__private.core.commands.data_retrieval.update_node_data.models import NodeData


@dataclass(kw_only=True)
class ShowAccount(WorldBasedCommand):
    account_name: str
    _account_data: NodeData = field(init=False)
    _account_alarms: AlarmsStorage = field(init=False)

    async def fetch_data(self) -> None:
        account = TrackedAccount(name=self.account_name)
        await self.world.commands.update_node_data(accounts=[account])
        await self.world.commands.update_alarms_data(accounts=[account])

        self._account_data = account.data
        self._account_alarms = account.alarms

    async def _run(self) -> None:
        general_info_table = self._create_general_info_table()
        balances_table = self._create_balance_table()
        manabar_stats_table = self._create_manabar_stats_table()
        grouped_tables = Group(general_info_table, Padding(""), balances_table, Padding(""), manabar_stats_table)
        columned_tables = Columns([grouped_tables], title=f"Details of '{self.account_name}' account")
        print_cli(columned_tables)

    def _get_account_type_name(self) -> str | None:
        if self.profile.accounts.is_account_working(self.account_name):
            return "Tracked account (working)"
        if self.profile.accounts.is_account_watched(self.account_name):
            return "Tracked account"
        return None

    def _create_general_info_table(self) -> Table:
        general_info_table = Table(title="General information", show_header=False)
        general_info_table.add_column("", justify="left", style="cyan", no_wrap=True)
        general_info_table.add_column("", justify="right", style="green", no_wrap=True)

        account_type = self._get_account_type_name()

        if account_type:
            general_info_table.add_row("Account type", account_type)
        general_info_table.add_row("Last history entry", humanize_datetime(self._account_data.last_history_entry))
        general_info_table.add_row("Account update", humanize_datetime(self._account_data.last_account_update))
        general_info_table.add_row("Number of new account token", str(self._account_data.pending_claimed_accounts))
        general_info_table.add_row("Number of alarms", str(len(self._account_alarms.harmful_alarms)))
        return general_info_table

    def _create_balance_table(self) -> Table:
        balances_table = Table(title="The balances")
        hive_symbol = Asset.get_symbol(Asset.Hive)
        hbd_symbol = Asset.get_symbol(Asset.Hbd)
        hp_symbol = "HP"
        balances_table.add_column("", justify="left", style="cyan", no_wrap=True)
        balances_table.add_column(hbd_symbol, justify="right", style="green", no_wrap=True)
        balances_table.add_column(hive_symbol, justify="right", style="green", no_wrap=True)
        balances_table.add_column(hp_symbol, justify="right", style="green", no_wrap=True)

        humanize_asset_no_symbol = partial(humanize_asset, show_symbol=False)

        balances_table.add_row(
            "Liquid",
            humanize_asset_no_symbol(self._account_data.hbd_balance),
            humanize_asset_no_symbol(self._account_data.hive_balance),
            humanize_hive_power_with_comma(self._account_data.owned_hp_balance.hp_balance, show_symbol=False),
        )
        balances_table.add_row(
            "Savings",
            humanize_asset_no_symbol(self._account_data.hbd_savings),
            humanize_asset_no_symbol(self._account_data.hive_savings),
            "---",
        )
        return balances_table

    def _create_manabar_stats_table(self) -> Table:
        manabar_stats_table = Table(title="Voting info")
        manabar_stats_table.add_column("", justify="left", style="cyan", no_wrap=True)
        manabar_stats_table.add_column("RC", justify="right", style="green", no_wrap=True)
        manabar_stats_table.add_column("Voting", justify="right", style="green", no_wrap=True)
        manabar_stats_table.add_column("Downvoting", justify="right", style="green", no_wrap=True)

        rc = self._account_data.rc_manabar_ensure
        vote = self._account_data.vote_manabar
        downvote = self._account_data.downvote_manabar

        full_regain_message = "How much time to be full again"
        manabar_stats_table.add_row(
            "Percent",
            humanize_percent(rc.percentage),
            humanize_percent(vote.percentage),
            humanize_percent(downvote.percentage),
        )
        manabar_stats_table.add_row(
            "Current mana",
            humanize_hive_power_with_comma(rc.value),
            humanize_hive_power_with_comma(vote.value),
            humanize_hive_power_with_comma(downvote.value),
        )
        manabar_stats_table.add_row(
            full_regain_message,
            humanize_manabar_regeneration_time(rc.full_regeneration),
            humanize_manabar_regeneration_time(vote.full_regeneration),
            humanize_manabar_regeneration_time(downvote.full_regeneration),
        )
        return manabar_stats_table
