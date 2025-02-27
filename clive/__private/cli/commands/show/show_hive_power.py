from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.console import Console, Group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core import iwax
from clive.__private.core.formatters.humanize import (
    align_to_dot,
    humanize_asset,
    humanize_bool,
    humanize_datetime,
    humanize_hive_power,
    humanize_hp_vests_apr,
    humanize_percent,
    humanize_vest_to_hive_ratio,
)
from clive.__private.core.percent_conversions import hive_percent_to_percent

if TYPE_CHECKING:
    from rich.console import RenderableType

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.core.formatters.humanize import SignPrefixT
    from clive.__private.models import HpVestsBalance


@dataclass(kw_only=True)
class ShowHivePower(WorldBasedCommand):
    account_name: str
    _hp_data: HivePowerData = field(init=False)

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        self._hp_data = wrapper.result_or_raise

        general_info = self.__general_info()
        apr = self.__apr()
        conversion_factor = self.__conversion_factor()
        next_withdrawal = self.__next_withdrawal()
        to_withdraw = self.__to_withdraw()
        withdraw_routes = self.__withdraw_routes()
        delegations = self.__delegations()

        left_group = Group(general_info, Padding(""), withdraw_routes, Padding(""), delegations)
        right_group = Group(next_withdrawal, Padding(""), to_withdraw, Padding(""), apr, conversion_factor)
        columns = Columns([left_group, right_group], title=f"Hive Power defails of `{self.account_name}` account")

        console = Console()
        console.print(columns)

    def __general_info(self) -> RenderableType:
        def add_row(table: Table, title: str, shares: HpVestsBalance, sign_prefix: SignPrefixT = "") -> None:
            table.add_row(
                title,
                f"{humanize_asset(shares.hp_balance, show_symbol=False, sign_prefix=sign_prefix)}",
                f"{humanize_asset(shares.vests_balance, show_symbol=False, sign_prefix=sign_prefix)}",
            )

        table_general_info = Table(title="Hive Power balance")
        table_general_info.add_column("Voting Power", justify="left", style="cyan", no_wrap=True)
        table_general_info.add_column("Amount [HP]", justify="right", style="green", no_wrap=True)
        table_general_info.add_column("Amount [VESTS]", justify="right", style="green", no_wrap=True)

        add_row(table_general_info, "Owned", self._hp_data.owned_balance)
        add_row(table_general_info, "Received", self._hp_data.received_balance, sign_prefix="+")
        add_row(table_general_info, "Delegated", self._hp_data.delegated_balance, sign_prefix="-")
        add_row(table_general_info, "Power Down", self._hp_data.next_power_down, sign_prefix="-")
        add_row(table_general_info, "Effective", self._hp_data.total_balance)
        return table_general_info

    def __apr(self) -> RenderableType:
        return f"{humanize_hp_vests_apr(self._hp_data.current_hp_apr, with_label=True)}"

    def __conversion_factor(self) -> RenderableType:
        factor = humanize_vest_to_hive_ratio(self._hp_data.gdpo, show_symbol=True)
        return f"HP is calculated to VESTS with the factor: 1.000 HP -> {factor}"

    def __next_withdrawal(self) -> RenderableType:
        hp = humanize_hive_power(self._hp_data.next_power_down.hp_balance)
        vests = humanize_asset(self._hp_data.next_power_down.vests_balance)

        amount_title = "Amount"
        hp_aligned, vests_aligned = align_to_dot(hp, vests, center_to=amount_title)

        table_next_withdrawal = Table(title="Next withdrawal of Hive Power")
        table_next_withdrawal.add_column(Text("Date", justify="center"), style="green", no_wrap=True)
        table_next_withdrawal.add_column(Text("Amount", justify="center"), style="green", no_wrap=True)

        table_next_withdrawal.add_row(
            humanize_datetime(self._hp_data.next_vesting_withdrawal),
            hp_aligned,
        )
        table_next_withdrawal.add_row("", vests_aligned)
        return table_next_withdrawal

    def __to_withdraw(self) -> RenderableType:
        table_to_withdraw = Table(title="Hive Power withdrawals summary")
        total_title = "Total"
        remaining_title = "Remains"
        table_to_withdraw.add_column(Text(total_title, justify="center"), style="green", no_wrap=True)
        table_to_withdraw.add_column(Text(remaining_title, justify="center"), style="green", no_wrap=True)

        total_hp = humanize_hive_power(self._hp_data.to_withdraw.hp_balance)
        total_vests = humanize_asset(self._hp_data.to_withdraw.vests_balance)
        total_hp_aligned, total_vests_aligned = align_to_dot(total_hp, total_vests, center_to=total_title)

        remaining_hp = humanize_hive_power(self._hp_data.remaining.hp_balance)
        remaining_vests = humanize_asset(self._hp_data.remaining.vests_balance)
        remaining_hp_aligned, remaining_vests_aligned = align_to_dot(
            remaining_hp, remaining_vests, center_to=remaining_title
        )

        table_to_withdraw.add_row(total_hp_aligned, remaining_hp_aligned)
        table_to_withdraw.add_row(total_vests_aligned, remaining_vests_aligned)
        return table_to_withdraw

    def __withdraw_routes(self) -> RenderableType:
        if len(self._hp_data.withdraw_routes) == 0:
            return colorize_content_not_available("There are no withdraw routes set")
        withdraw_routes_table = Table(title="Current withdraw routes")
        withdraw_routes_table.add_column("To", justify="left", style="cyan", no_wrap=True)
        withdraw_routes_table.add_column("Percent", justify="right", style="green", no_wrap=True)
        withdraw_routes_table.add_column("Auto vest", justify="right", style="green", no_wrap=True)

        for withdraw_route in self._hp_data.withdraw_routes:
            withdraw_route_percent = hive_percent_to_percent(withdraw_route.percent.value)
            withdraw_routes_table.add_row(
                withdraw_route.to_account,
                humanize_percent(withdraw_route_percent),
                humanize_bool(withdraw_route.auto_vest),
            )
        return withdraw_routes_table

    def __delegations(self) -> RenderableType:
        if len(self._hp_data.delegations) == 0:
            return colorize_content_not_available("There are no delegations set")

        delegations_title = "Current delegations"
        delegations_table = Table(title=delegations_title)
        delegations_table.add_column(Text("Delegatee", justify="center"), style="cyan", no_wrap=True)
        delegations_table.add_column(Text("Shares", justify="center"), style="green", no_wrap=True)

        for delegation in self._hp_data.delegations:
            delegation_hp_raw = iwax.calculate_vests_to_hp(delegation.vesting_shares, self._hp_data.gdpo)
            delegation_hp = humanize_hive_power(delegation_hp_raw)
            delegation_vests = humanize_asset(delegation.vesting_shares)
            hp_aligned, vests_aligned = align_to_dot(delegation_hp, delegation_vests, center_to=delegations_title)

            delegations_table.add_row(delegation.delegatee, hp_aligned)
            delegations_table.add_row("", vests_aligned, end_section=True)
        return delegations_table
