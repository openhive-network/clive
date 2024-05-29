from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_data_retrieval import CommandDataRetrieval
from clive.models.aliased import FindRecurrentTransfers as SchemasFindRecurrentTransfers
from clive.models.aliased import TransferSchedule

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node

ScheduledTransfers = list[TransferSchedule]


class FindScheduledTransfersError(CommandError):
    pass


class FindScheduledTransfersFromAccountMismatchError(FindScheduledTransfersError):
    account_name: str
    transfer_schedule: TransferSchedule

    def __init__(self, command: Command, account_name: str, transfer_schedule: TransferSchedule):
        self.account_name = account_name
        self.transfer_schedule = transfer_schedule
        self.reason = f"Wrong from account '{self.transfer_schedule.from_}' should be '{self.account_name}'."
        super().__init__(command=command, reason=self.reason)


@dataclass
class AllowedSorts:
    id: Final[str] = "id"
    trigger_data: Final[str] = "trigger_date"
    to: Final[str] = "to"
    amount: Final[str] = "amount"
    memo: Final[str] = "memo"
    recurrence: Final[str] = "recurrence"
    consecutive_failures: Final[str] = "consecutive_failures"
    remaining_executions: Final[str] = "remaining_executions"
    pair_id: Final[str] = "pair_id"


@dataclass(kw_only=True)
class FindScheduledTransfers(
    CommandDataRetrieval[SchemasFindRecurrentTransfers, SchemasFindRecurrentTransfers, ScheduledTransfers]
):
    node: Node
    account_name: str

    async def _harvest_data_from_api(self) -> SchemasFindRecurrentTransfers:
        return await self.node.api.database_api.find_recurrent_transfers(from_=self.account_name)

    async def _sanitize_data(self, data: SchemasFindRecurrentTransfers) -> SchemasFindRecurrentTransfers:
        self._assert_from_account(data)
        return data

    async def _process_data(self, data: SchemasFindRecurrentTransfers) -> ScheduledTransfers:
        return data.recurrent_transfers

    def _assert_from_account(self, data: SchemasFindRecurrentTransfers) -> None:
        for recurrent_transfer in data.recurrent_transfers:
            if recurrent_transfer.from_ != self.account_name:
                raise FindScheduledTransfersFromAccountMismatchError(
                    self, account_name=self.account_name, transfer_schedule=recurrent_transfer
                )
