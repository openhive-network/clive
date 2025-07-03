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
    from clive.__private.models.schemas import SavingsWithdrawal


@dataclass(kw_only=True)
class ShowPendingWithdrawals(WorldBasedCommand):
    """
    Show pending withdrawals for a savings account.

    Args:
        account_name: The name of the savings account to retrieve pending withdrawals for.
    """

    account_name: str

    async def _run(self) -> None:
        """
        Retrieve and display pending withdrawals for the specified savings account.

        This method fetches the pending transfers from the savings account and displays them in a formatted table.
        The table includes details such as the recipient, amount, completion time, memo, and request ID.
        If there are no pending withdrawals, a message is printed indicating that there are none available.

        Returns:
            None: This method does not return any value. It prints the results table directly to the console.
        """
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

        transfer: SavingsWithdrawal
        for transfer in result.pending_transfers:
            table.add_row(
                f"{transfer.to}",
                f"{Asset.to_legacy(transfer.amount)}",
                f"{humanize_datetime(transfer.complete)}",
                f"{transfer.memo}",
                f"{transfer.request_id}",
            )
        console.print(table)
