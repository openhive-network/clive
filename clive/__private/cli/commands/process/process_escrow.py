from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import EscrowInvalidDeadlineError, EscrowNotFoundError, EscrowZeroAmountError
from clive.__private.models.schemas import (
    EscrowApproveOperation,
    EscrowDisputeOperation,
    EscrowReleaseOperation,
    EscrowTransferOperation,
    HiveDateTime,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import ComposeTransaction
    from clive.__private.core.commands.data_retrieval.escrow_data import EscrowData, EscrowInfo
    from clive.__private.models.asset import Asset


@dataclass(kw_only=True)
class ProcessEscrowTransfer(OperationCommand):
    from_account: str
    to: str
    agent: str
    escrow_id: int | None
    hbd_amount: Asset.Hbd
    hive_amount: Asset.Hive
    fee: Asset.LiquidT
    ratification_deadline: datetime
    escrow_expiration: datetime
    json_meta: str = ""

    @property
    def escrow_id_ensure(self) -> int:
        assert self.escrow_id is not None, "escrow_id should be set at this point"
        return self.escrow_id

    async def validate(self) -> None:
        self._validate_amounts()
        self._validate_deadlines()
        await super().validate()

    def _validate_amounts(self) -> None:
        """Validate that at least one amount is non-zero."""
        if int(self.hbd_amount.amount) == 0 and int(self.hive_amount.amount) == 0:
            raise EscrowZeroAmountError

    def _validate_deadlines(self) -> None:
        """Validate that deadlines are in the future and properly ordered."""
        now = datetime.now(UTC)
        ratification = self.ratification_deadline
        expiration = self.escrow_expiration

        # Make datetimes timezone-aware if they're naive
        if ratification.tzinfo is None:
            ratification = ratification.replace(tzinfo=UTC)
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=UTC)

        if ratification <= now:
            raise EscrowInvalidDeadlineError("Ratification deadline must be in the future.")

        if expiration <= now:
            raise EscrowInvalidDeadlineError("Escrow expiration must be in the future.")

        if expiration <= ratification:
            raise EscrowInvalidDeadlineError("Escrow expiration must be after ratification deadline.")

    async def fetch_data(self) -> None:
        await super().fetch_data()
        if self.escrow_id is None:
            wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.from_account)
            escrow_data: EscrowData = wrapper.result_or_raise
            self.escrow_id = escrow_data.create_escrow_id()

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowTransferOperation(
            from_=self.from_account,
            to=self.to,
            agent=self.agent,
            escrow_id=self.escrow_id_ensure,
            hbd_amount=self.hbd_amount,
            hive_amount=self.hive_amount,
            fee=self.fee,
            ratification_deadline=HiveDateTime(self.ratification_deadline),
            escrow_expiration=HiveDateTime(self.escrow_expiration),
            json_meta=self.json_meta,
        )


@dataclass(kw_only=True)
class ProcessEscrowApprove(OperationCommand):
    from_account: str
    to: str | None
    agent: str | None
    who: str
    escrow_id: int
    approve: bool = True

    @property
    def to_ensure(self) -> str:
        assert self.to is not None, "to should be set at this point"
        return self.to

    @property
    def agent_ensure(self) -> str:
        assert self.agent is not None, "agent should be set at this point"
        return self.agent

    async def fetch_data(self) -> None:
        await super().fetch_data()
        await self._fill_escrow_data_if_needed()

    async def _fill_escrow_data_if_needed(self) -> None:
        """Fetch escrow data from blockchain if to or agent is not provided."""
        if self.to is None or self.agent is None:
            escrow = await self._get_escrow_from_blockchain()
            if self.to is None:
                self.to = escrow.to
            if self.agent is None:
                self.agent = escrow.agent

    async def _get_escrow_from_blockchain(self) -> EscrowInfo:
        """Fetch escrow from blockchain and return it."""
        wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.from_account)
        escrow_data: EscrowData = wrapper.result_or_raise
        escrow = escrow_data.get_escrow_by_id(self.escrow_id)
        if escrow is None:
            raise EscrowNotFoundError(self.from_account, self.escrow_id)
        return escrow

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowApproveOperation(
            from_=self.from_account,
            to=self.to_ensure,
            agent=self.agent_ensure,
            who=self.who,
            escrow_id=self.escrow_id,
            approve=self.approve,
        )


@dataclass(kw_only=True)
class ProcessEscrowDispute(OperationCommand):
    from_account: str
    to: str | None
    agent: str | None
    who: str
    escrow_id: int

    @property
    def to_ensure(self) -> str:
        assert self.to is not None, "to should be set at this point"
        return self.to

    @property
    def agent_ensure(self) -> str:
        assert self.agent is not None, "agent should be set at this point"
        return self.agent

    async def fetch_data(self) -> None:
        await super().fetch_data()
        await self._fill_escrow_data_if_needed()

    async def _fill_escrow_data_if_needed(self) -> None:
        """Fetch escrow data from blockchain if to or agent is not provided."""
        if self.to is None or self.agent is None:
            escrow = await self._get_escrow_from_blockchain()
            if self.to is None:
                self.to = escrow.to
            if self.agent is None:
                self.agent = escrow.agent

    async def _get_escrow_from_blockchain(self) -> EscrowInfo:
        """Fetch escrow from blockchain and return it."""
        wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.from_account)
        escrow_data: EscrowData = wrapper.result_or_raise
        escrow = escrow_data.get_escrow_by_id(self.escrow_id)
        if escrow is None:
            raise EscrowNotFoundError(self.from_account, self.escrow_id)
        return escrow

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowDisputeOperation(
            from_=self.from_account,
            to=self.to_ensure,
            agent=self.agent_ensure,
            who=self.who,
            escrow_id=self.escrow_id,
        )


@dataclass(kw_only=True)
class ProcessEscrowRelease(OperationCommand):
    from_account: str
    to: str | None
    agent: str | None
    who: str
    receiver: str
    escrow_id: int
    hbd_amount: Asset.Hbd
    hive_amount: Asset.Hive

    @property
    def to_ensure(self) -> str:
        assert self.to is not None, "to should be set at this point"
        return self.to

    @property
    def agent_ensure(self) -> str:
        assert self.agent is not None, "agent should be set at this point"
        return self.agent

    async def fetch_data(self) -> None:
        await super().fetch_data()
        await self._fill_escrow_data_if_needed()

    async def _fill_escrow_data_if_needed(self) -> None:
        """Fetch escrow data from blockchain if to or agent is not provided."""
        if self.to is None or self.agent is None:
            escrow = await self._get_escrow_from_blockchain()
            if self.to is None:
                self.to = escrow.to
            if self.agent is None:
                self.agent = escrow.agent

    async def _get_escrow_from_blockchain(self) -> EscrowInfo:
        """Fetch escrow from blockchain and return it."""
        wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.from_account)
        escrow_data: EscrowData = wrapper.result_or_raise
        escrow = escrow_data.get_escrow_by_id(self.escrow_id)
        if escrow is None:
            raise EscrowNotFoundError(self.from_account, self.escrow_id)
        return escrow

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowReleaseOperation(
            from_=self.from_account,
            to=self.to_ensure,
            agent=self.agent_ensure,
            who=self.who,
            receiver=self.receiver,
            escrow_id=self.escrow_id,
            hbd_amount=self.hbd_amount,
            hive_amount=self.hive_amount,
        )
