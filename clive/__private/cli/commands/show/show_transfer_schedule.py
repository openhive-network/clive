from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Final, TypeVar

from rich.columns import Columns
from rich.console import Console, Group
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.styling import colorize_content_not_available
from clive.__private.core.commands.data_retrieval.find_scheduled_transfers import AllowedSorts, ScheduledTransfers
from clive.__private.core.formatters.humanize import align_to_dot, humanize_asset, humanize_datetime
from clive.__private.core.shorthand_timedelta import timedelta_to_shorthand_timedelta
from clive.__private.storage.accounts import Account
from clive.__private.storage.mock_database import NodeData
from clive.models.asset import Asset

if TYPE_CHECKING:
    from clive.models.aliased import TransferSchedule


@dataclass
class FutureTransferSchedule:
    trigger_date: datetime
    to: str
    amount: Asset.Hive | Asset.Hbd
    memo: str
    recurrence: int
    remaining_executions: int
    pair_id: int
    possible_amount: Asset.Hive | Asset.Hbd
    from_: str


FutureScheduledTransfers = list[FutureTransferSchedule]

Sortable = TypeVar("Sortable", ScheduledTransfers, "FutureScheduledTransfers")

ERROR_LACK_OF_FUNDS_MESSAGE_RAW: Final[str] = "Possible lack of funds."
DEFAULT_FUTURE_DEEPTH: Final[int] = 10
LACK_OF_FUNDS_AMOUNT: Final[Asset.Hive] = Asset.hive(0)


@dataclass(kw_only=True)
class ShowTransferSchedule(WorldBasedCommand):
    account_name: str

    async def _run(self) -> None:
        account = Account(name=self.account_name)
        (await self.world.commands.update_node_data(accounts=[account])).raise_if_error_occurred()
        data = account.data

        scheduled_transfers = (
            await self.world.commands.find_scheduled_transfers(account_name=self.account_name)
        ).result_or_raise

        console = Console()

        if not scheduled_transfers:
            console.print(colorize_content_not_available(f"Account `{self.account_name}` has no scheduled transfers."))
            return

        table_definitions = self.__create_table_definition(scheduled_transfers)
        table_upcoming = self.__create_table_upcoming(scheduled_transfers, data)

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

        scheduled_transfer: TransferSchedule
        sorted_scheduled_transfers = self.get_sorted_by(
            scheduled_transfers, sort_by=[AllowedSorts.to, AllowedSorts.pair_id]
        )

        aligned_amounts = align_to_dot(
            *[humanize_asset(scheduled_transfer.amount) for scheduled_transfer in sorted_scheduled_transfers],
            center_to=amount_column_name,
        )

        for idx, scheduled_transfer in enumerate(sorted_scheduled_transfers):
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

    def __create_table_upcoming(self, scheduled_transfers: ScheduledTransfers, data: NodeData) -> Table:
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

        future_scheduled_transfer: FutureTransferSchedule
        future_scheduled_transfers = self.get_future_scheduled_transfers(scheduled_transfers, data)
        amount_to_align = [humanize_asset(future_transfer.amount) for future_transfer in future_scheduled_transfers]
        possible_amount_to_align = [
            humanize_asset(future_transfer.possible_amount) for future_transfer in future_scheduled_transfers
        ]

        amount_aligned = align_to_dot(*amount_to_align, center_to=amount_column_name)
        possible_amount_aligned = align_to_dot(*possible_amount_to_align, center_to=possible_amount_column_name)

        for idx, future_scheduled_transfer in enumerate(future_scheduled_transfers):
            possible_amount: Text | str = (
                Text(f"{ERROR_LACK_OF_FUNDS_MESSAGE_RAW}", style="red", justify="center")
                if future_scheduled_transfer.possible_amount == LACK_OF_FUNDS_AMOUNT
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

    def get_future_scheduled_transfers(
        self,
        scheduled_transfers: ScheduledTransfers,
        data: NodeData,
        deepth: int = DEFAULT_FUTURE_DEEPTH,
    ) -> FutureScheduledTransfers:
        future_scheduled_transfers: FutureScheduledTransfers = []
        for scheduled_transfer in scheduled_transfers:
            for idx, remains in enumerate(range(min(scheduled_transfer.remaining_executions, deepth))):
                amount = scheduled_transfer.amount * idx
                future_scheduled_transfer = FutureTransferSchedule(
                    trigger_date=scheduled_transfer.trigger_date + timedelta(hours=idx * scheduled_transfer.recurrence),
                    from_=scheduled_transfer.from_,
                    to=scheduled_transfer.to,
                    amount=scheduled_transfer.amount,
                    possible_amount=(
                        data.hive_balance - amount if data.hive_balance > amount else LACK_OF_FUNDS_AMOUNT
                    ),
                    memo=scheduled_transfer.memo,
                    recurrence=scheduled_transfer.recurrence,
                    remaining_executions=remains,
                    pair_id=scheduled_transfer.pair_id,
                )
                future_scheduled_transfers.append(future_scheduled_transfer)
        return self.get_sorted_by(future_scheduled_transfers, sort_by=[AllowedSorts.trigger_data])

    def get_sorted_by(self, scheduled_transfers: Sortable, sort_by: list[str]) -> Sortable:
        import operator

        return sorted(scheduled_transfers, key=operator.attrgetter(*sort_by))
