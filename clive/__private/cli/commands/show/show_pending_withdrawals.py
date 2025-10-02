from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli, print_content_not_available
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models.asset import Asset

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.__private.models.schemas import SavingsWithdrawal


@dataclass(kw_only=True)
class ShowPendingWithdrawals(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.retrieve_savings_data(account_name=self.account_name)
        result: SavingsData = wrapper.result_or_raise

        if not result.pending_transfers:
            print_content_not_available(f"Account `{self.account_name}` has no pending withdrawals")
            return

        table = Table(title=f"Pending withdrawals of `{self.account_name}` account")

        table.add_column("To", justify="left", style="cyan", no_wrap=True)
        table.add_column("Amount", justify="right", style="green", no_wrap=True)
        table.add_column("Realized on (UTC)", justify="right", style="green", no_wrap=True)
        table.add_column("Memo", justify="right", style="green", no_wrap=True)
        table.add_column("RequestId", justify="right", style="green", no_wrap=True)

        transfer: SavingsWithdrawal
        for transfer in result.pending_transfers:
            table.add_row(
                f"{transfer.to}",
                f"{Asset.to_legacy(transfer.amount)}",
                f"{humanize_datetime(transfer.complete)}",
                f"{transfer.memo}",
                f"{transfer.request_id}",
            )
        print_cli(table)
