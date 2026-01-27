from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.escrow_data import EscrowData, EscrowInfo


@dataclass(kw_only=True)
class ShowEscrow(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.account_name)
        result: EscrowData = wrapper.result_or_raise

        if not result.escrows:
            print_content_not_available(f"Account `{self.account_name}` has no escrows")
            return

        table = Table(title=f"Escrows for account: {self.account_name}")

        table.add_column("Escrow ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("To", justify="left", style="green", no_wrap=True)
        table.add_column("Agent", justify="left", style="green", no_wrap=True)
        table.add_column("HBD Balance", justify="right", style="green", no_wrap=True)
        table.add_column("HIVE Balance", justify="right", style="green", no_wrap=True)
        table.add_column("Status", justify="center", style="yellow", no_wrap=True)
        table.add_column("Ratification (UTC)", justify="right", style="green", no_wrap=True)
        table.add_column("Expiration (UTC)", justify="right", style="green", no_wrap=True)

        escrow_info: EscrowInfo
        for escrow_info in result.escrows:
            table.add_row(
                f"{escrow_info.escrow_id}",
                f"{escrow_info.to}",
                f"{escrow_info.agent}",
                f"{Asset.to_legacy(escrow_info.hbd_balance)}",
                f"{Asset.to_legacy(escrow_info.hive_balance)}",
                f"{escrow_info.status}",
                f"{humanize_datetime(escrow_info.ratification_deadline)}",
                f"{humanize_datetime(escrow_info.escrow_expiration)}",
            )
        print_cli(table)
