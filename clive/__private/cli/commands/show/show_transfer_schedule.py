from dataclasses import dataclass
from datetime import timedelta
from typing import Final

from rich.columns import Columns
from rich.console import Console, Group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core.commands.data_retrieval.find_scheduled_transfers import ScheduledTransfers
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.core.shorthand_timedelta import timedelta_to_shorthand_timedelta

ERROR_LACK_OF_FUNDS_MESSAGE_RAW: Final[str] = "Possible lack of funds."
DEFAULT_FUTURE_DEEPTH: Final[int] = 10


@dataclass(kw_only=True)
class ShowTransferSchedule(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        scheduled_transfers = (
            await self.world.commands.find_scheduled_transfers(account_name=self.account_name)
        ).result_or_raise

        console = Console()

        if not scheduled_transfers.scheduled_transfers:
            console.print(colorize_content_not_available(f"Account `{self.account_name}` has no scheduled transfers."))
            return

        table_definitions = self.__create_table_definition(scheduled_transfers)
        table_upcoming = self.__create_table_upcoming(scheduled_transfers)

        table_definitions_group = Group(table_definitions, Padding(""))
        table_upcoming_group = Group(table_upcoming, Padding(""))

        show_transfer_schedule = Columns([table_definitions_group, table_upcoming_group])
        console.print(show_transfer_schedule)

    def __create_table_definition(self, scheduled_transfers: ScheduledTransfers) -> Table:
        """Create table with definitions."""
        table_definitions = Table(title=f"Transfer schedule definitions for `{self.account_name}` account")

        amount_column_name = "Amount"
        table_definitions.add_column("From", justify="center", style="cyan", no_wrap=True)
        table_definitions.add_column("To", justify="center", style="cyan", no_wrap=True)
        table_definitions.add_column("Pair id", justify="center", style="cyan", no_wrap=True)
        table_definitions.add_column(Text(amount_column_name, justify="center"), style="green", no_wrap=True)
        table_definitions.add_column("Memo", justify="center", style="green", no_wrap=True)
        table_definitions.add_column("Next", justify="center", style="green", no_wrap=True)
        table_definitions.add_column("Frequency", justify="center", style="green", no_wrap=True)
        table_definitions.add_column("Remaining", justify="center", style="green", no_wrap=True)
        table_definitions.add_column("Failures", justify="center", style="green", no_wrap=True)

        scheduled_transfers.sort_by(sort_by=["to", "pair_id"])
        aligned_amounts = scheduled_transfers.get_amount_aligned_to_dot()
        for idx, scheduled_transfer in enumerate(scheduled_transfers.scheduled_transfers):
            table_definitions.add_row(
                scheduled_transfer.from_,
                scheduled_transfer.to,
                str(scheduled_transfer.pair_id),
                str(aligned_amounts[idx]),
                scheduled_transfer.memo,
                humanize_datetime(scheduled_transfer.trigger_date),
                timedelta_to_shorthand_timedelta(timedelta(hours=scheduled_transfer.recurrence)),
                str(scheduled_transfer.remaining_executions),
                str(scheduled_transfer.consecutive_failures),
            )
        return table_definitions

    def __create_table_upcoming(self, scheduled_transfers: ScheduledTransfers) -> Table:
        """Create table with upcoming scheduled transfers."""
        table_upcoming = Table(
            title=f"Next {DEFAULT_FUTURE_DEEPTH} upcoming recurrent transfers for `{self.account_name}` account"
        )

        amount_column_name = "Amount"
        possible_amount_column_name = "Possible balance after operation"
        table_upcoming.add_column("From", justify="center", style="cyan", no_wrap=True)
        table_upcoming.add_column("To", justify="center", style="cyan", no_wrap=True)
        table_upcoming.add_column("Pair id", justify="center", style="cyan", no_wrap=True)
        table_upcoming.add_column(Text(amount_column_name, justify="center"), style="green", no_wrap=True)
        table_upcoming.add_column(Text(possible_amount_column_name, justify="center"), style="green", no_wrap=True)
        table_upcoming.add_column("Memo", justify="center", style="green", no_wrap=True)
        table_upcoming.add_column("Next", justify="center", style="green", no_wrap=True)
        table_upcoming.add_column("Frequency", justify="center", style="green", no_wrap=True)

        future_scheduled_transfers = scheduled_transfers.get_future_scheduled_transfers(deepth=DEFAULT_FUTURE_DEEPTH)
        future_scheduled_transfers.sort_by(["trigger_date"])
        amount_aligned = future_scheduled_transfers.get_amount_aligned_to_dot(center_to=amount_column_name)
        possible_amount_aligned = future_scheduled_transfers.get_possibly_amount_aligned_to_dot(
            center_to=possible_amount_column_name
        )

        for idx, future_scheduled_transfer in enumerate(future_scheduled_transfers.future_scheduled_transfers):
            possible_amount: Text | str = (
                Text(f"{ERROR_LACK_OF_FUNDS_MESSAGE_RAW}", style="red", justify="center")
                if future_scheduled_transfer.is_lack_of_funds()
                else possible_amount_aligned[idx]
            )
            table_upcoming.add_row(
                future_scheduled_transfer.from_,
                future_scheduled_transfer.to,
                str(future_scheduled_transfer.pair_id),
                amount_aligned[idx],
                possible_amount,
                future_scheduled_transfer.memo,
                str(future_scheduled_transfer.trigger_date),
                timedelta_to_shorthand_timedelta(timedelta(hours=future_scheduled_transfer.recurrence)),
            )
        return table_upcoming
