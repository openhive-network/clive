from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.console import Group
from rich.padding import Padding
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core import iwax
from clive.__private.core.formatters.humanize import (
    align_to_dot,
    humanize_asset,
    humanize_hive_power,
    humanize_percent,
    humanize_timedelta,
)

if TYPE_CHECKING:
    from rich.console import RenderableType

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.core.commands.data_retrieval.rc_data import RcData
    from clive.__private.core.formatters.humanize import SignPrefixT


@dataclass(kw_only=True)
class ShowRc(WorldBasedCommand):
    account_name: str
    _rc_data: RcData = field(init=False)
    _hp_data: HivePowerData = field(init=False)

    async def _run(self) -> None:
        rc_wrapper = await self.world.commands.retrieve_rc_data(account_name=self.account_name)
        self._rc_data = rc_wrapper.result_or_raise

        hp_wrapper = await self.world.commands.retrieve_hp_data(account_name=self.account_name)
        self._hp_data = hp_wrapper.result_or_raise

        summary = self.__summary()
        manabar_info = self.__manabar_info()
        delegations = self.__delegations()

        left_group = Group(summary, Padding(""), delegations)
        right_group = Group(manabar_info)
        columns = Columns([left_group, right_group], title=f"Resource Credits of `{self.account_name}` account")

        print_cli(columns)

    def _add_dual_row(  # noqa: PLR0913
        self,
        table: Table,
        label: str,
        rc_amount: int,
        *,
        sign_prefix: SignPrefixT = "",
        column_title: str = "",
        end_section: bool = False,
    ) -> None:
        hp = humanize_hive_power(iwax.calculate_vests_to_hp(rc_amount, self._hp_data.gdpo))
        vests = humanize_asset(iwax.vests(rc_amount))
        hp_aligned, vests_aligned = align_to_dot(hp, vests, center_to=column_title)

        if sign_prefix and rc_amount != 0:
            hp_aligned = f"{sign_prefix}{hp_aligned.lstrip()}"
            vests_aligned = f"{sign_prefix}{vests_aligned.lstrip()}"

        table.add_row(label, hp_aligned)
        table.add_row("", vests_aligned, end_section=end_section)

    def __summary(self) -> RenderableType:
        amount_title = "Amount"
        table = Table(title="Resource Credits balance")
        table.add_column("RC Source", justify="left", style="cyan", no_wrap=True)
        table.add_column(amount_title, justify="right", style="green", no_wrap=True)

        self._add_dual_row(table, "From stake", self._rc_data.owned_rc_from_stake, column_title=amount_title)
        self._add_dual_row(
            table, "Delegated out", self._rc_data.delegated_rc, sign_prefix="-", column_title=amount_title
        )
        self._add_dual_row(
            table, "Received", self._rc_data.received_delegated_rc, sign_prefix="+", column_title=amount_title
        )
        self._add_dual_row(table, "Max RC", self._rc_data.max_rc, column_title=amount_title)
        return table

    def __manabar_info(self) -> RenderableType:
        value_title = "Value"
        table = Table(title="RC Manabar")
        table.add_column("Property", justify="left", style="cyan", no_wrap=True)
        table.add_column(value_title, justify="right", style="green", no_wrap=True)

        self._add_dual_row(table, "Current RC", self._rc_data.current_mana, column_title=value_title)
        table.add_row("RC Percentage", humanize_percent(self._rc_data.rc_percentage))
        table.add_row("Full regeneration in", humanize_timedelta(self._rc_data.full_regeneration))
        return table

    def __delegations(self) -> RenderableType:
        if len(self._rc_data.outgoing_delegations) == 0:
            return colorize_content_not_available("No outgoing RC delegations")

        delegations_title = "Current outgoing RC delegations"
        table = Table(title=delegations_title)
        table.add_column("Delegatee", justify="left", style="cyan", no_wrap=True)
        table.add_column("RC Amount", justify="right", style="green", no_wrap=True)

        for delegation in self._rc_data.outgoing_delegations:
            self._add_dual_row(
                table,
                str(delegation.to),
                int(delegation.delegated_rc),
                column_title=delegations_title,
                end_section=True,
            )
        return table
