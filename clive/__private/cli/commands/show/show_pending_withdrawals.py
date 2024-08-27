from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.models import Asset

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.savings_data import SavingsData
    from clive.__private.models.aliased import SavingsWithdrawals


@dataclass(kw_only=True)
class ShowPendingWithdrawals(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        console = Console()
        wrapper = await self.world.commands.retrieve_savings_data(account_name=self.account_name)
        result: SavingsData = wrapper.result_or_raise

        if not result.pending_transfers:
            message = f"Account `{self.account_name}` has no pending withdrawals"
            console.print(colorize_content_not_available(message))
            return

        table = Table(title=f"Pending withdrawals of `{self.account_name}` account")

        table.add_column("To", justify="left", style="cyan", no_wrap=True)
        table.add_column("Amount", justify="right", style="green", no_wrap=True)
        table.add_column("Realized on (UTC)", justify="right", style="green", no_wrap=True)
        table.add_column("Memo", justify="right", style="green", no_wrap=True)
        table.add_column("RequestId", justify="right", style="green", no_wrap=True)

        transfer: SavingsWithdrawals
        for transfer in result.pending_transfers:
            table.add_row(
                f"{transfer.to}",
                f"{Asset.to_legacy(transfer.amount)}",
                f"{humanize_datetime(transfer.complete)}",
                f"{transfer.memo}",
                f"{transfer.request_id}",
            )
        console.print(table)
