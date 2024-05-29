from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Final

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    ProcessTransferScheduleAlreadyExistsError,
    ProcessTransferScheduleDoesNotExistsError,
    ProcessTransferScheduleInvalidAmountError,
    ProcessTransferScheduleNoScheduledTransfersError,
    ProcessTransferScheduleNullPairIdError,
    ProcessTransferScheduleTooLongLifetimeError,
)
from clive.__private.core.constants import SCHEDULED_TRANSFER_TWO_YEARS_MAX_LIFETIME_DURATION_IN_HOURS
from clive.__private.core.shorthand_timedelta import timedelta_to_shorthand_timedelta
from clive.models import Asset
from clive.models.aliased import RecurrentTransferOperation, TransferSchedule

REMOVE_VALUE_HIVE: Final[Asset.Hive] = Asset.hive(0)
REMOVE_VALUE_HBD: Final[Asset.Hbd] = Asset.hbd(0)
REMOVE_VALUES: Final[list[Asset.Hive | Asset.Hbd]] = [REMOVE_VALUE_HIVE, REMOVE_VALUE_HBD]


@dataclass(kw_only=True)
class ProcessTransferSchedule(OperationCommand):
    from_account: str
    to: str

    def _create_recurent_transfer_pair_id_extension(self, pair_id: int) -> list[Any]:
        return [{"type": "recurrent_transfer_pair_id", "value": {"pair_id": pair_id}}] if pair_id > 0 else []

    async def fetch_scheduled_transfers_for_current_account(self) -> list[TransferSchedule]:
        """Get all scheduled transfers (recurrent transfers) for current account from blockchain."""
        wrapper = await self.world.commands.find_scheduled_transfers(account_name=self.from_account)
        return wrapper.result_or_raise

    def get_scheduled_transfer(
        self, pair_id: int, scheduled_transfers: list[TransferSchedule]
    ) -> TransferSchedule | None:
        """Get target `to` scheduled transfer (recurrent transfer) from the fetched collection."""
        for st in scheduled_transfers:
            if st.to == self.to and st.pair_id == pair_id:
                return st
        return None

    def validate_existence(
        self, pair_id: int, scheduled_transfer: TransferSchedule | None, should_exists: bool
    ) -> None:
        """Validate if scheduled_transfer (recurrent transfer) exists."""
        exists = scheduled_transfer is not None
        if exists == should_exists:
            return
        if exists:
            raise ProcessTransferScheduleAlreadyExistsError(self.to, pair_id)
        raise ProcessTransferScheduleDoesNotExistsError(self.to, pair_id)

    def validate_any_existence(self, scheduled_transfers: list[TransferSchedule]) -> None:
        """Validate if there are any scheduled transfers (recurrent transfers) from current account."""
        if scheduled_transfers:
            return
        raise ProcessTransferScheduleNoScheduledTransfersError(self.from_account)

    def validate_amount(self, amount: Asset.LiquidT) -> None:
        """Validate amount for create, and modify calls - it should be different than values from REMOVE_VALUES."""
        if amount in REMOVE_VALUES:
            raise ProcessTransferScheduleInvalidAmountError

    def validate_pair_id(self, scheduled_transfer: list[TransferSchedule], pair_id: int | None) -> None:
        """Validate if pair_id is set, when there is more than one recurrent transfers."""
        number_of_scheduled_transfers = len(scheduled_transfer)
        if number_of_scheduled_transfers > 1 and pair_id is None:
            raise ProcessTransferScheduleNullPairIdError

    def validate_existance_lifetime(self, repeat: int, frequency: int) -> None:
        scheduled_transfer_lifetime = repeat * frequency
        if scheduled_transfer_lifetime > SCHEDULED_TRANSFER_TWO_YEARS_MAX_LIFETIME_DURATION_IN_HOURS:
            raise ProcessTransferScheduleTooLongLifetimeError(
                requested_lifetime=timedelta_to_shorthand_timedelta(timedelta(hours=scheduled_transfer_lifetime))
            )


@dataclass(kw_only=True)
class ProcessTransferScheduleCreate(ProcessTransferSchedule):
    amount: Asset.LiquidT
    memo: str
    frequency: int
    repeat: int
    pair_id: int

    async def _create_operation(self) -> RecurrentTransferOperation:
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
            recurrence=self.frequency,
            executions=self.repeat,
            extensions=self._create_recurent_transfer_pair_id_extension(self.pair_id),
        )

    async def validate_inside_context_manager(self) -> None:
        scheduled_transfers = await self.fetch_scheduled_transfers_for_current_account()

        if scheduled_transfers:
            scheduled_transfer = self.get_scheduled_transfer(self.pair_id, scheduled_transfers)
            self.validate_existence(self.pair_id, scheduled_transfer, False)
        await super().validate_inside_context_manager()

    async def validate(self) -> None:
        self.validate_amount(self.amount)
        self.validate_existance_lifetime(self.repeat, self.frequency)
        await super().validate()


@dataclass(kw_only=True)
class ProcessTransferScheduleModify(ProcessTransferSchedule):
    scheduled_transfer: TransferSchedule | None = field(default=None, init=False)
    amount: Asset.LiquidT | None = None
    memo: str | None = None
    frequency: int | None = None
    repeat: int | None = None
    pair_id: int | None = None

    async def _create_operation(self) -> RecurrentTransferOperation:
        assert self.scheduled_transfer is not None, "Scheduled transfer should be there, validation is done before"
        assert self.pair_id is not None, "Pair id should be there, validation is done before"
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
            recurrence=self.frequency,
            executions=self.repeat,
            extensions=self._create_recurent_transfer_pair_id_extension(self.pair_id),
        )

    async def _run(self) -> None:
        assert self.scheduled_transfer is not None, "Scheduled transfer should be there, validation is done before"
        self.amount = self.amount if self.amount else self.scheduled_transfer.amount
        self.repeat = self.repeat if self.repeat else self.scheduled_transfer.remaining_executions
        self.frequency = self.frequency if self.frequency else self.scheduled_transfer.recurrence
        self.memo = self.memo if self.memo else self.scheduled_transfer.memo
        self.validate_existance_lifetime(self.repeat, self.frequency)
        await super()._run()

    async def validate_inside_context_manager(self) -> None:
        scheduled_transfers = await self.fetch_scheduled_transfers_for_current_account()
        self.validate_any_existence(scheduled_transfers)
        self.validate_pair_id(scheduled_transfers, self.pair_id)

        self.pair_id = 0 if self.pair_id is None else self.pair_id
        scheduled_transfer = self.get_scheduled_transfer(self.pair_id, scheduled_transfers)

        self.validate_existence(self.pair_id, scheduled_transfer, True)
        self.scheduled_transfer = scheduled_transfer
        await super().validate_inside_context_manager()

    async def validate(self) -> None:
        if self.amount:
            self.validate_amount(self.amount)
        if self.frequency and self.repeat:
            self.validate_existance_lifetime(self.repeat, self.frequency)
        await super().validate()


@dataclass(kw_only=True)
class ProcessTransferScheduleRemove(ProcessTransferSchedule):
    scheduled_transfer: TransferSchedule | None = field(default=None, init=False)
    pair_id: int | None = None

    async def _create_operation(self) -> RecurrentTransferOperation:
        assert self.scheduled_transfer is not None, "Scheduled transfer should be there, validation is done before"
        assert self.pair_id is not None, "Pair id should be there, validation is done before"
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=REMOVE_VALUE_HIVE,
            memo=self.scheduled_transfer.memo,
            recurrence=self.scheduled_transfer.recurrence,
            executions=self.scheduled_transfer.remaining_executions,
            extensions=self._create_recurent_transfer_pair_id_extension(self.pair_id),
        )

    async def validate_inside_context_manager(self) -> None:
        scheduled_transfers = await self.fetch_scheduled_transfers_for_current_account()
        self.validate_any_existence(scheduled_transfers)
        self.validate_pair_id(scheduled_transfers, self.pair_id)

        self.pair_id = 0 if self.pair_id is None else self.pair_id
        scheduled_transfer = self.get_scheduled_transfer(self.pair_id, scheduled_transfers)

        self.validate_existence(self.pair_id, scheduled_transfer, True)
        self.scheduled_transfer = scheduled_transfer
        await super().validate_inside_context_manager()
