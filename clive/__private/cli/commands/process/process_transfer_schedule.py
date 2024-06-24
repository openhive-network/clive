from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    ProcessTransferScheduleAlreadyExistsError,
    ProcessTransferScheduleDoesNotExistsError,
    ProcessTransferScheduleInvalidAmountError,
    ProcessTransferScheduleNoScheduledTransfersError,
    ProcessTransferScheduleNullPairIdError,
    ProcessTransferScheduleTooLongLifetimeError,
)
from clive.__private.core.constants.node import (
    SCHEDULED_TRANSFER_MAX_LIFETIME,
    VALUE_TO_REMOVE_SCHEDULED_TRANSFER,
)
from clive.__private.core.shorthand_timedelta import timedelta_to_int_hours
from clive.models import Asset
from clive.models.aliased import (
    RecurrentTransferOperation,
    RecurrentTransferPairIdOperationExtension,
    RecurrentTransferPairIdRepresentation,
)

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.find_scheduled_transfers import (
        ScheduledTransfer,
        ScheduledTransfers,
    )

SCHEDULED_TRANSFER_REMOVE_VALUES: Final[list[Asset.Hive | Asset.Hbd]] = [
    Asset.hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
    Asset.hbd(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
]


@dataclass(kw_only=True)
class ProcessTransferSchedule(OperationCommand):
    scheduled_transfers: ScheduledTransfers | None = field(default=None, init=False)
    from_account: str
    to: str
    pair_id: int | None = None

    @property
    def scheduled_transfer(self) -> ScheduledTransfer | None:
        return self.get_scheduled_transfer()

    async def fetch_data(self) -> None:
        self.scheduled_transfers = await self.fetch_scheduled_transfers_for_current_account()

    def _create_recurent_transfer_pair_id_extension(self) -> list[Any]:
        # TODO: This will be removed after hf28, because pair_id will be mandatory
        if self.pair_id is None or self.pair_id == 0:
            return []

        recurent_transfer_extension = RecurrentTransferPairIdOperationExtension(pair_id=self.pair_id)
        extension = RecurrentTransferPairIdRepresentation(
            type=recurent_transfer_extension.get_name(), value=recurent_transfer_extension
        )
        return [extension.dict(by_alias=True)]

    def _identity_check(self, scheduled_transfer: ScheduledTransfer) -> bool:
        """Determine if a scheduled transfer matches destination and the specified pair ID."""
        pair_id = 0 if self.pair_id is None else self.pair_id
        return scheduled_transfer.to == self.to and scheduled_transfer.pair_id == pair_id

    async def fetch_scheduled_transfers_for_current_account(self) -> ScheduledTransfers:
        """Get all scheduled transfers (recurrent transfers) for current account from blockchain."""
        return (await self.world.commands.find_scheduled_transfers(account_name=self.from_account)).result_or_raise

    def get_scheduled_transfer(self) -> ScheduledTransfer | None:
        """Get target `to` scheduled transfer (recurrent transfer) from the fetched collection."""
        if self.scheduled_transfers:
            for st in self.scheduled_transfers.get_scheduled_transfers():
                if self._identity_check(st):
                    return st
        return None

    def validate_existence(self, *, should_exists: bool) -> None:
        """Validate if scheduled_transfer (recurrent transfer) exists."""
        exists = self.scheduled_transfer is not None
        pair_id = 0 if self.pair_id is None else self.pair_id
        if exists == should_exists:
            return
        if exists:
            raise ProcessTransferScheduleAlreadyExistsError(self.to, pair_id)
        raise ProcessTransferScheduleDoesNotExistsError(self.to, pair_id)

    def validate_any_existence(self) -> None:
        """Validate if there are any scheduled transfers (recurrent transfers) from current account."""
        if self.scheduled_transfers:
            return
        raise ProcessTransferScheduleNoScheduledTransfersError(self.from_account)

    def validate_pair_id(self) -> None:
        """Validate if pair_id is set, when there is more than one recurrent transfers."""
        assert self.scheduled_transfers is not None, "There are no scheduled transfers."
        number_of_scheduled_transfers = len(self.scheduled_transfers.get_scheduled_transfers())
        if number_of_scheduled_transfers > 1 and self.pair_id is None:
            raise ProcessTransferScheduleNullPairIdError


@dataclass(kw_only=True)
class ProcessTransferScheduleWithExtendedValidation(ProcessTransferSchedule):
    amount: Asset.LiquidT | None
    memo: str | None
    frequency: timedelta | None
    repeat: int | None

    def validate_amount(self) -> None:
        """
        Validate amount for create, and modify calls.

        It should be different than values from SCHEDULED_TRANSFER_REMOVE_VALUES.
        """
        if self.amount in SCHEDULED_TRANSFER_REMOVE_VALUES:
            raise ProcessTransferScheduleInvalidAmountError

    def validate_existence_lifetime(self) -> None:
        assert self.repeat is not None, "Value of repeat should be known."
        assert self.frequency is not None, "Value of repeat should be known."
        scheduled_transfer_lifetime = self.repeat * self.frequency
        if scheduled_transfer_lifetime > SCHEDULED_TRANSFER_MAX_LIFETIME:
            raise ProcessTransferScheduleTooLongLifetimeError(requested_lifetime=scheduled_transfer_lifetime)


@dataclass(kw_only=True)
class ProcessTransferScheduleCreate(ProcessTransferScheduleWithExtendedValidation):
    amount: Asset.LiquidT
    memo: str
    frequency: timedelta
    repeat: int

    async def _create_operation(self) -> RecurrentTransferOperation:
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
            recurrence=timedelta_to_int_hours(self.frequency),
            executions=self.repeat,
            extensions=self._create_recurent_transfer_pair_id_extension(),
        )

    async def validate_inside_context_manager(self) -> None:
        if self.scheduled_transfers:
            self.validate_existence(should_exists=False)
        await super().validate_inside_context_manager()

    async def validate(self) -> None:
        self.validate_amount()
        self.validate_existence_lifetime()
        await super().validate()


@dataclass(kw_only=True)
class ProcessTransferScheduleModify(ProcessTransferScheduleWithExtendedValidation):
    async def _create_operation(self) -> RecurrentTransferOperation:
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
            recurrence=self.configured_frequency,
            executions=self.repeat,
            extensions=self.configured_extensions,
        )

    async def _configure_inside_context_manager(self) -> None:
        assert self.frequency is not None, "Value of frequency is known at this point."
        self.configured_frequency = timedelta_to_int_hours(self.frequency)
        self.configured_extensions = self._create_recurent_transfer_pair_id_extension()

    async def fetch_data(self) -> None:
        self.scheduled_transfers = await self.fetch_scheduled_transfers_for_current_account()
        if self.scheduled_transfer:
            self.amount = self.amount if self.amount is not None else self.scheduled_transfer.amount
            self.repeat = self.repeat if self.repeat is not None else self.scheduled_transfer.remaining_executions
            self.frequency = (
                self.frequency if self.frequency is not None else timedelta(hours=self.scheduled_transfer.recurrence)
            )
            self.memo = self.memo if self.memo is not None else self.scheduled_transfer.memo

    async def validate_inside_context_manager(self) -> None:
        self.validate_any_existence()
        assert self.scheduled_transfers is not None, "Value of scheduled_transfers is known at this point."
        self.validate_pair_id()
        self.validate_existence(should_exists=True)
        self.validate_existence_lifetime()
        await super().validate_inside_context_manager()

    async def validate(self) -> None:
        if self.amount:
            self.validate_amount()
        if self.frequency and self.repeat:
            self.validate_existence_lifetime()
        await super().validate()


@dataclass(kw_only=True)
class ProcessTransferScheduleRemove(ProcessTransferSchedule):
    async def _create_operation(self) -> RecurrentTransferOperation:
        assert self.scheduled_transfer is not None, "Scheduled transfer should be there, validation is done before"
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=Asset.hive(VALUE_TO_REMOVE_SCHEDULED_TRANSFER),
            memo=self.scheduled_transfer.memo,
            recurrence=self.scheduled_transfer.recurrence,
            executions=self.scheduled_transfer.remaining_executions,
            extensions=self.configured_extensions,
        )

    async def fetch_data(self) -> None:
        self.scheduled_transfers = await self.fetch_scheduled_transfers_for_current_account()

    async def _configure_inside_context_manager(self) -> None:
        self.configured_extensions = self._create_recurent_transfer_pair_id_extension()

    async def validate_inside_context_manager(self) -> None:
        self.validate_any_existence()
        self.validate_pair_id()
        self.validate_existence(should_exists=True)
        await super().validate_inside_context_manager()
