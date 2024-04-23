from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.console import Console, Group
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.calculate_vests_to_hive_ratio import calulcate_vests_to_hive_ratio
from clive.__private.core.formatters.humanize import humanize_asset, humanize_bool, humanize_datetime
from clive.__private.core.hive_vests_conversions import vests_to_hive

if TYPE_CHECKING:
    from rich.console import RenderableType

    from clive.__private.core.commands.data_retrieval.hive_power_data import SharesBalance
    from clive.__private.core.formatters.humanize import SignPrefixT


@dataclass(kw_only=True)
class ShowHivePower(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        self.hp_data = wrapper.result_or_raise

        general_info = self.__general_info()
        apr = self.__apr()
        conversion_factor = self.__conversion_factor()
        power_down_info = self.__power_down_info()
        withdraw_routes = self.__withdraw_routes()
        delegations = self.__delegations()

        left_group = Group(general_info, withdraw_routes, delegations)
        right_group = Group(power_down_info, apr, conversion_factor)
        columns = Columns([left_group, right_group])

        console = Console()
        console.print(columns)

    def __general_info(self) -> RenderableType:
        table_general_info = Table(title=f"Hive Power for account `{self.account_name}`", expand=True)
        table_general_info.add_column("Voting Power", justify="left", style="cyan", no_wrap=True)
        table_general_info.add_column("Amount in HP", justify="right", style="green", no_wrap=True)
        table_general_info.add_column("Amount in VESTS", justify="right", style="green", no_wrap=True)

        def add_row(table: Table, title: str, shares: SharesBalance, sign_prefix: SignPrefixT = "") -> None:
            table.add_row(
                title,
                f"{humanize_asset(shares.hp_balance, show_symbol=False, sign_prefix=sign_prefix)}",
                f"{humanize_asset(shares.vests_balance, show_symbol=False, sign_prefix=sign_prefix)}",
            )

        add_row(table_general_info, "Owned", self.hp_data.owned_balance)
        add_row(table_general_info, "Received", self.hp_data.received_balance, sign_prefix="+")
        add_row(table_general_info, "Delegated", self.hp_data.delegated_balance, sign_prefix="-")
        add_row(table_general_info, "Power Down", self.hp_data.next_power_down, sign_prefix="-")
        add_row(table_general_info, "Effective", self.hp_data.total_balance)
        return table_general_info

    def __apr(self) -> RenderableType:
        return f"APR interest for HP/VESTS ≈ {self.hp_data.current_hp_apr} %"

    def __conversion_factor(self) -> RenderableType:
        factor = calulcate_vests_to_hive_ratio(self.hp_data.gdpo)
        return f"HP is calculated to VESTS with the factor: 1.000 HP -> {factor} VESTS"

    def __power_down_info(self) -> RenderableType:
        table_power_down_info = Table(title=f"Power down info for account `{self.account_name}`", expand=True)
        table_power_down_info.add_column("Next withdrawal", justify="left", style="green", no_wrap=True)
        table_power_down_info.add_column("To withdraw", justify="left", style="green", no_wrap=True)

        table_power_down_info.add_row(
            humanize_datetime(self.hp_data.next_vesting_withdrawal),
            f"{humanize_asset(self.hp_data.to_withdraw.hp_balance, show_symbol=False)} HP \n"
            f"{humanize_asset(self.hp_data.to_withdraw.vests_balance, show_symbol=False)} VESTS \n",
        )
        return table_power_down_info

    def __withdraw_routes(self) -> RenderableType:
        if len(self.hp_data.withdraw_routes) == 0:
            return f"There are no withdraw routes for account `{self.account_name}`"
        withdraw_routes_table = Table(expand=True, title=f"Current withdraw routes for account `{self.account_name}`")
        withdraw_routes_table.add_column("To", justify="left", style="cyan", no_wrap=True)
        withdraw_routes_table.add_column("Percent", justify="right", style="green", no_wrap=True)
        withdraw_routes_table.add_column("Auto vest", justify="right", style="green", no_wrap=True)

        for withdraw_route in self.hp_data.withdraw_routes:
            withdraw_routes_table.add_row(
                withdraw_route.to_account,
                f"{withdraw_route.percent / 100} %",
                f"{humanize_bool(withdraw_route.auto_vest)}",
            )
        return withdraw_routes_table

    def __delegations(self) -> RenderableType:
        if len(self.hp_data.delegations) == 0:
            return f"There are no delegations for account `{self.account_name}`"

        delegations_table = Table(expand=True, title=f"Current delegations for account `{self.account_name}`")
        delegations_table.add_column("Delegatee", justify="left", style="cyan", no_wrap=True)
        delegations_table.add_column("Shares in HP", justify="right", style="green", no_wrap=True)
        delegations_table.add_column("Shares in VESTS", justify="right", style="green", no_wrap=True)

        for delegation in self.hp_data.delegations:
            delegation_amount_hive = vests_to_hive(delegation.vesting_shares, self.hp_data.gdpo)
            delegations_table.add_row(
                delegation.delegatee,
                f"{humanize_asset(delegation_amount_hive, show_symbol=False)}",
                f"{humanize_asset(delegation.vesting_shares, show_symbol=False)}",
            )
        return delegations_table
