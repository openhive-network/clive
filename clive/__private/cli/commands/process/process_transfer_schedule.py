from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    ProcessTransferScheduleAlreadyExistsError,
    ProcessTransferScheduleDoesNotExistsError,
    ProcessTransferScheduleInvalidAmountError,
    ProcessTransferScheduleNullPairIdError,
    ProcessTransferScheduleTooLongLifetimeError,
)
from clive.__private.core.constants.node import (
    SCHEDULED_TRANSFER_MAX_LIFETIME,
    SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
)
from clive.__private.core.constants.node_special_assets import SCHEDULED_TRANSFER_REMOVE_ASSETS
from clive.__private.core.date_utils import timedelta_to_int_hours
from clive.__private.models.schemas import (
    RecurrentTransferOperation,
    RecurrentTransferPairIdExtension,
    RecurrentTransferPairIdRepresentation,
)

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.find_scheduled_transfers import (
        AccountScheduledTransferData,
        ScheduledTransfer,
    )
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class _ProcessTransferScheduleCommon(OperationCommand, ABC):
    """
    Class for common logic of processing transfer schedule commands.

    Args:
        account_scheduled_transfers_data: Data containing scheduled transfers for the account.
        from_account: The account from which the transfer is initiated.
        to: The destination account for the transfer.
        pair_id: Optional identifier for the transfer pair.
    """

    account_scheduled_transfers_data: AccountScheduledTransferData = field(init=False)
    from_account: str
    to: str
    pair_id: int | None = None

    @property
    def scheduled_transfer(self) -> ScheduledTransfer | None:
        """
        Get the scheduled transfer that matches the destination and pair ID.

        Returns:
            ScheduledTransfer | None: The matching scheduled transfer or None if not found.
        """
        if self.account_scheduled_transfers_data.has_any_scheduled_transfers():
            for st in self.account_scheduled_transfers_data.scheduled_transfers:
                if self._identity_check(st):
                    return st
        return None

    @property
    def scheduled_transfer_ensure(self) -> ScheduledTransfer:
        """
        Get the scheduled transfer, ensuring it exists.

        Raises:
            AssertionError: If the scheduled transfer is None.

        Returns:
            ScheduledTransfer: The scheduled transfer that matches the destination and pair ID.
        """
        assert self.scheduled_transfer is not None, "Scheduled transfer should be there, validation is done before"
        return self.scheduled_transfer

    def _create_recurrent_transfer_pair_id_extension(self) -> list[Any]:
        """
        Create a list of extensions for the recurrent transfer operation.

        Returns:
            list: A list containing the RecurrentTransferPairIdRepresentation extension.
        """
        # TODO: This will be removed after hf28, because pair_id will be mandatory
        if self.pair_id is None or self.pair_id == 0:
            return []

        recurrent_transfer_extension = RecurrentTransferPairIdExtension(pair_id=self.pair_id)
        extension = RecurrentTransferPairIdRepresentation(
            type=recurrent_transfer_extension.get_name(), value=recurrent_transfer_extension
        )
        return [extension.dict(by_alias=True)]

    def _identity_check(self, scheduled_transfer: ScheduledTransfer) -> bool:
        """
        Check if the scheduled transfer matches the destination and pair ID.

        Args:
            scheduled_transfer: The scheduled transfer to check.

        Returns:
            bool: True if the scheduled transfer matches the destination and pair ID, False otherwise.
        """
        """Determine if a scheduled transfer matches destination and the specified pair ID."""
        pair_id = 0 if self.pair_id is None else self.pair_id
        return scheduled_transfer.to == self.to and scheduled_transfer.pair_id == pair_id

    async def fetch_data(self) -> None:
        """
        Fetch data for the current account's scheduled transfers.

        Returns:
            None
        """
        self.account_scheduled_transfers_data = await self.fetch_scheduled_transfers_for_current_account()

    async def fetch_scheduled_transfers_for_current_account(self) -> AccountScheduledTransferData:
        """
        Get all scheduled transfers (recurrent transfers) for current account from blockchain.

        Returns:
            AccountScheduledTransferData: Data containing scheduled transfers for the account.
        """
        return (await self.world.commands.find_scheduled_transfers(account_name=self.from_account)).result_or_raise

    def validate_existence(self, *, should_exists: bool) -> None:
        """
        Validate if scheduled_transfer (recurrent transfer) exists.

        Args:
            should_exists: Whether the scheduled transfer should exist or not.

        Raises:
            ProcessTransferScheduleAlreadyExistsError: If the scheduled transfer already exists when it shouldn't.
            ProcessTransferScheduleDoesNotExistsError: If the scheduled transfer does not exist when it should.

        Returns:
            None
        """
        exists = self.scheduled_transfer is not None
        pair_id = 0 if self.pair_id is None else self.pair_id
        if exists == should_exists:
            return
        if exists:
            raise ProcessTransferScheduleAlreadyExistsError(self.to, pair_id)
        raise ProcessTransferScheduleDoesNotExistsError(self.to, pair_id)

    def validate_pair_id_should_be_given(self) -> None:
        """
        Validate if pair_id is set, when there is more than one recurrent transfers.

        Raises:
            ProcessTransferScheduleNullPairIdError: If pair_id is None when there are multiple scheduled transfers.

        Returns:
            None
        """
        if (
            self.account_scheduled_transfers_data.has_mutiple_scheduled_transfers_to_receiver(self.to)
            and self.pair_id is None
        ):
            raise ProcessTransferScheduleNullPairIdError


@dataclass(kw_only=True)
class _ProcessTransferScheduleCreateModifyCommon(_ProcessTransferScheduleCommon):
    """
    Class for common logic of processing transfer schedule.

    Args:
        amount: The amount of the asset to be transferred.
        memo: Optional memo for the transfer.
        frequency: The frequency of the transfer as a timedelta.
        repeat: The number of times the transfer should be repeated.
    """

    amount: Asset.LiquidT | None
    memo: str | None
    frequency: timedelta | None
    repeat: int | None

    @property
    def frequency_ensure(self) -> timedelta:
        """
        Ensure that frequency is set, otherwise raise an assertion error.

        Raises:
            AssertionError: If frequency is None.

        Returns:
            timedelta: The frequency of the transfer.
        """
        assert self.frequency is not None, "Value of frequency is known at this point."
        return self.frequency

    def validate_amount_not_a_removal_value(self) -> None:
        """
        Validate amount for create, and modify calls.

        It should be different than values from SCHEDULED_TRANSFER_REMOVE_ASSETS.

        Raises:
            ProcessTransferScheduleInvalidAmountError: If the amount is in SCHEDULED_TRANSFER_REMOVE_ASSETS.

        Returns:
            None
        """
        if self.amount in SCHEDULED_TRANSFER_REMOVE_ASSETS:
            raise ProcessTransferScheduleInvalidAmountError

    def validate_existence_lifetime(self) -> None:
        """
        Validate existence lifetime of the scheduled transfer.

        Raises:
            ProcessTransferScheduleTooLongLifetimeError: If the scheduled transfer lifetime exceeds the maximum allowed.
            AssertionError: If repeat or frequency is None.

        Returns:
            None
        """
        assert self.repeat is not None, "Value of repeat should be known."
        assert self.frequency is not None, "Value of repeat should be known."
        scheduled_transfer_lifetime = self.repeat * self.frequency
        if scheduled_transfer_lifetime > SCHEDULED_TRANSFER_MAX_LIFETIME:
            raise ProcessTransferScheduleTooLongLifetimeError(requested_lifetime=scheduled_transfer_lifetime)

    async def _create_operation(self) -> RecurrentTransferOperation:
        """
        Create a RecurrentTransferOperation for the scheduled transfer.

        Returns:
            RecurrentTransferOperation: The operation representing the scheduled transfer.
        """
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self.amount,
            memo=self.memo,
            recurrence=timedelta_to_int_hours(self.frequency_ensure),
            executions=self.repeat,
            extensions=self._create_recurrent_transfer_pair_id_extension(),
        )


@dataclass(kw_only=True)
class ProcessTransferScheduleCreate(_ProcessTransferScheduleCreateModifyCommon):
    """
    Class for processing transfer schedule creation.

    Args:
        amount: The amount of the asset to be transferred.
        memo: Optional memo for the transfer.
        frequency: The frequency of the transfer as a timedelta.
        repeat: The number of times the transfer should be repeated.
    """

    amount: Asset.LiquidT
    memo: str
    frequency: timedelta
    repeat: int

    async def validate_inside_context_manager(self) -> None:
        """
        Validate inside context manager for creation of a scheduled transfer.

        Returns:
            None
        """
        self.validate_existence(should_exists=False)
        await super().validate_inside_context_manager()

    async def validate(self) -> None:
        """
        Validate the creation of a scheduled transfer.

        Returns:
            None
        """
        self.validate_amount_not_a_removal_value()
        self.validate_existence_lifetime()
        await super().validate()


@dataclass(kw_only=True)
class ProcessTransferScheduleModify(_ProcessTransferScheduleCreateModifyCommon):
    """Class for processing transfer schedule modification."""

    async def fetch_data(self) -> None:
        """
        Fetch data for the current account's scheduled transfers.

        This method retrieves the scheduled transfers for the current account and sets the
        attributes for amount, repeat, frequency, and memo based on the existing scheduled transfer.
        If the scheduled transfer already exists, it initializes the attributes with the values from the existing
        transfer.
        If the scheduled transfer does not exist, it initializes the attributes with None or default values.

        Returns:
            None
        """
        self.account_scheduled_transfers_data = await self.fetch_scheduled_transfers_for_current_account()
        if self.scheduled_transfer:
            self.amount = self.amount if self.amount is not None else self.scheduled_transfer.amount
            self.repeat = self.repeat if self.repeat is not None else self.scheduled_transfer.remaining_executions
            self.frequency = (
                self.frequency if self.frequency is not None else timedelta(hours=self.scheduled_transfer.recurrence)
            )
            self.memo = self.memo if self.memo is not None else self.scheduled_transfer.memo

    async def validate_inside_context_manager(self) -> None:
        """
        Validate inside context manager for modification of a scheduled transfer.

        Returns:
            None
        """
        self.validate_existence(should_exists=True)
        self.validate_pair_id_should_be_given()
        self.validate_existence_lifetime()
        await super().validate_inside_context_manager()

    async def validate(self) -> None:
        """
        Validate the modification of a scheduled transfer.

        This method checks if the amount is not a removal value, and if the frequency and repeat are set,

        Returns:
            None
        """
        if self.amount:
            self.validate_amount_not_a_removal_value()
        if self.frequency and self.repeat:
            self.validate_existence_lifetime()
        await super().validate()


@dataclass(kw_only=True)
class ProcessTransferScheduleRemove(_ProcessTransferScheduleCommon):
    """Class for processing transfer schedule removal."""

    async def _create_operation(self) -> RecurrentTransferOperation:
        """
        Create an operation for removing a scheduled transfer.

        Returns:
            RecurrentTransferOperation: The operation representing the removal of the scheduled transfer.
        """
        return RecurrentTransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=SCHEDULED_TRANSFER_REMOVE_ASSETS[0].copy(),
            memo=self.scheduled_transfer_ensure.memo,
            recurrence=self.scheduled_transfer_ensure.recurrence,
            # We can't rewrite the executions value.
            # In case when remaining_executions will be less than SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
            # broadcast will fail.
            executions=SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
            extensions=self._create_recurrent_transfer_pair_id_extension(),
        )

    async def validate_inside_context_manager(self) -> None:
        """
        Validate inside context manager for removal of a scheduled transfer.

        Returns:
            None
        """
        self.validate_existence(should_exists=True)
        self.validate_pair_id_should_be_given()
        await super().validate_inside_context_manager()
