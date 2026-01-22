from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.convert_data import ConvertData


@dataclass(kw_only=True)
class ShowPendingConvert(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_convert_data(account_name=self.account_name)
        result: ConvertData = wrapper.result_or_raise

        has_hbd_conversions = bool(result.hbd_conversions)
        has_collateralized_conversions = bool(result.collateralized_conversions)

        if not has_hbd_conversions and not has_collateralized_conversions:
            print_content_not_available(f"Account `{self.account_name}` has no pending conversions")
            return

        if has_hbd_conversions:
            self._print_hbd_conversions_table(result)

        if has_collateralized_conversions:
            self._print_collateralized_conversions_table(result)

    def _print_hbd_conversions_table(self, result: ConvertData) -> None:
        table = Table(title=f"Pending HBD → HIVE conversions of `{self.account_name}` account")

        table.add_column("RequestId", justify="right", style="cyan", no_wrap=True)
        table.add_column("Amount", justify="right", style="green", no_wrap=True)
        table.add_column("Conversion Date (UTC)", justify="right", style="green", no_wrap=True)

        for conversion in result.hbd_conversions:
            table.add_row(
                f"{conversion.request_id}",
                f"{Asset.to_legacy(conversion.amount)}",
                f"{humanize_datetime(conversion.conversion_date)}",
            )
        print_cli(table)

    def _print_collateralized_conversions_table(self, result: ConvertData) -> None:
        table = Table(title=f"Pending HIVE → HBD conversions of `{self.account_name}` account")

        table.add_column("RequestId", justify="right", style="cyan", no_wrap=True)
        table.add_column("Collateral", justify="right", style="green", no_wrap=True)
        table.add_column("Converted", justify="right", style="green", no_wrap=True)
        table.add_column("Conversion Date (UTC)", justify="right", style="green", no_wrap=True)

        for conversion in result.collateralized_conversions:
            table.add_row(
                f"{conversion.request_id}",
                f"{Asset.to_legacy(conversion.collateral_amount)}",
                f"{Asset.to_legacy(conversion.converted_amount)}",
                f"{humanize_datetime(conversion.conversion_date)}",
            )
        print_cli(table)
