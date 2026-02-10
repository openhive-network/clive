from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import (
    EscrowAgentReceiverRequiredError,
    EscrowAlreadyApprovedError,
    EscrowInvalidDeadlineError,
    EscrowNotApprovedError,
    EscrowNotFoundError,
    EscrowOperationNotAllowedForRoleError,
    EscrowReleaseNotAllowedError,
    EscrowRoleDetectionError,
    EscrowZeroAmountError,
)
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
    from clive.__private.core.types import EscrowRole
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
    ratification_deadline: datetime | timedelta
    escrow_expiration: datetime | timedelta
    json_meta: str = ""

    _head_block_time: datetime | None = None

    @property
    def escrow_id_ensure(self) -> int:
        assert self.escrow_id is not None, "escrow_id should be set at this point"
        return self.escrow_id

    @property
    def head_block_time(self) -> datetime:
        assert self._head_block_time is not None, "head_block_time should be set at this point"
        return self._head_block_time

    async def validate(self) -> None:
        self._validate_amounts()
        await super().validate()

    async def validate_inside_context_manager(self) -> None:
        await super().validate_inside_context_manager()
        await self._validate_deadlines()

    def _validate_amounts(self) -> None:
        """Validate that at least one amount is non-zero."""
        if int(self.hbd_amount.amount) == 0 and int(self.hive_amount.amount) == 0:
            raise EscrowZeroAmountError

    async def _validate_deadlines(self) -> None:
        """Validate that deadlines are in the future and properly ordered."""
        now = self.head_block_time
        ratification = self.ratification_deadline
        expiration = self.escrow_expiration

        assert isinstance(ratification, datetime), "ratification_deadline should be resolved to datetime at this point"
        assert isinstance(expiration, datetime), "escrow_expiration should be resolved to datetime at this point"

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

        gdpo = await self.world.node.api.database_api.get_dynamic_global_properties()
        self._head_block_time = gdpo.time.replace(tzinfo=UTC)

        if isinstance(self.ratification_deadline, timedelta):
            self.ratification_deadline = self.head_block_time + self.ratification_deadline
        if isinstance(self.escrow_expiration, timedelta):
            self.escrow_expiration = self.head_block_time + self.escrow_expiration

        if self.escrow_id is None:
            wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.from_account)
            escrow_data: EscrowData = wrapper.result_or_raise
            self.escrow_id = escrow_data.create_escrow_id()

    async def _create_operations(self) -> ComposeTransaction:
        assert isinstance(self.ratification_deadline, datetime), "should be resolved at this point"
        assert isinstance(self.escrow_expiration, datetime), "should be resolved at this point"

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
class ProcessEscrowWithRoleDetection(OperationCommand):
    """Base class for escrow operations requiring role detection."""

    escrow_owner: str
    escrow_id: int
    who_override: str

    # Class variable - override in subclasses to specify valid roles
    _valid_roles: ClassVar[tuple[EscrowRole, ...]]

    # Auto-filled from blockchain
    _escrow_info: EscrowInfo | None = None
    _detected_role: EscrowRole | None = None

    @property
    def escrow_info(self) -> EscrowInfo:
        assert self._escrow_info is not None, "escrow_info should be set at this point"
        return self._escrow_info

    @property
    def detected_role(self) -> EscrowRole:
        assert self._detected_role is not None, "detected_role should be set at this point"
        return self._detected_role

    @property
    @abstractmethod
    def _operation_name(self) -> str:
        """Return operation name for error messages (e.g., 'approve/reject', 'dispute', 'release')."""

    @property
    def _account_for_role_detection(self) -> str:
        """Get the account to use for role detection."""
        return self.who_override

    async def fetch_data(self) -> None:
        await super().fetch_data()
        await self._fetch_escrow_from_blockchain()
        self._detected_role = self._detect_role()

    async def _fetch_escrow_from_blockchain(self) -> None:
        """Fetch escrow data from blockchain."""
        wrapper = await self.world.commands.retrieve_escrow_data(account_name=self.escrow_owner)
        escrow_data: EscrowData = wrapper.result_or_raise
        escrow = escrow_data.get_escrow_by_id(self.escrow_id)
        if escrow is None:
            raise EscrowNotFoundError(self.escrow_owner, self.escrow_id)
        self._escrow_info = escrow

    def _detect_role(self) -> EscrowRole:
        """Detect role based on account and valid roles for this operation."""
        account = self._account_for_role_detection
        escrow = self.escrow_info

        role_map: dict[str, EscrowRole] = {
            escrow.from_: "sender",
            escrow.to: "receiver",
            escrow.agent: "agent",
        }

        if account not in role_map:
            # Account is not a party to this escrow at all
            raise EscrowRoleDetectionError(account, escrow.from_, escrow.to, escrow.agent)

        role = role_map[account]
        if role not in self._valid_roles:
            # Account is a party but this role cannot perform this operation
            raise EscrowOperationNotAllowedForRoleError(role, self._operation_name, self._valid_roles)

        return role

    def _role_to_who(self) -> str:
        """Convert detected role to the 'who' account name."""
        escrow = self.escrow_info
        role = self.detected_role
        who_map: dict[EscrowRole, str] = {
            "sender": escrow.from_,
            "receiver": escrow.to,
            "agent": escrow.agent,
        }
        return who_map[role]


@dataclass(kw_only=True)
class ProcessEscrowApprove(ProcessEscrowWithRoleDetection):
    """Process escrow approve/reject operation with automatic role detection."""

    _valid_roles: ClassVar[tuple[EscrowRole, ...]] = ("receiver", "agent")

    approve: bool = True

    @property
    def _operation_name(self) -> str:
        return "approve/reject"

    async def validate_inside_context_manager(self) -> None:
        """Validate that the role hasn't already approved (only when approving, not rejecting)."""
        await super().validate_inside_context_manager()
        if self.approve:
            self._validate_not_already_approved()

    def _validate_not_already_approved(self) -> None:
        """Check that the current role hasn't already approved."""
        role = self.detected_role
        escrow = self.escrow_info

        if role == "receiver" and escrow.to_approved:
            raise EscrowAlreadyApprovedError("receiver")
        if role == "agent" and escrow.agent_approved:
            raise EscrowAlreadyApprovedError("agent")

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowApproveOperation(
            from_=self.escrow_owner,
            to=self.escrow_info.to,
            agent=self.escrow_info.agent,
            who=self._role_to_who(),
            escrow_id=self.escrow_id,
            approve=self.approve,
        )


@dataclass(kw_only=True)
class ProcessEscrowDispute(ProcessEscrowWithRoleDetection):
    """Process escrow dispute operation with automatic role detection."""

    _valid_roles: ClassVar[tuple[EscrowRole, ...]] = ("sender", "receiver")

    @property
    def _operation_name(self) -> str:
        return "dispute"

    async def validate_inside_context_manager(self) -> None:
        """Validate that the escrow is fully approved before allowing dispute."""
        await super().validate_inside_context_manager()
        self._validate_escrow_approved()

    def _validate_escrow_approved(self) -> None:
        """Check that both agent and receiver have approved."""
        escrow = self.escrow_info
        if not (escrow.to_approved and escrow.agent_approved):
            raise EscrowNotApprovedError

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowDisputeOperation(
            from_=self.escrow_owner,
            to=self.escrow_info.to,
            agent=self.escrow_info.agent,
            who=self._role_to_who(),
            escrow_id=self.escrow_id,
        )


@dataclass(kw_only=True)
class ProcessEscrowRelease(ProcessEscrowWithRoleDetection):
    """Process escrow release operation with automatic role detection and receiver auto-fill."""

    _valid_roles: ClassVar[tuple[EscrowRole, ...]] = ("sender", "receiver", "agent")

    hbd_amount: Asset.Hbd
    hive_amount: Asset.Hive
    receiver: str | None = None  # Auto-filled for sender/receiver, required for agent

    @property
    def _operation_name(self) -> str:
        return "release"

    # Additional auto-filled field
    _resolved_receiver: str | None = None

    @property
    def resolved_receiver(self) -> str:
        assert self._resolved_receiver is not None, "resolved_receiver should be set at this point"
        return self._resolved_receiver

    async def fetch_data(self) -> None:
        await super().fetch_data()
        self._resolved_receiver = self._resolve_receiver()

    async def validate_inside_context_manager(self) -> None:
        """Validate release rules based on escrow state."""
        await super().validate_inside_context_manager()
        await self._validate_release_allowed()

    async def _validate_release_allowed(self) -> None:
        """
        Validate release rules based on escrow state.

        Rules:
        - Disputed: only agent can release
        - Non-disputed, before expiration: sender→receiver or receiver→sender only (cross-release)
        - Non-disputed, after expiration: anyone can release to anyone
        """
        escrow = self.escrow_info
        role = self.detected_role
        receiver = self.resolved_receiver

        if escrow.disputed:
            if role != "agent":
                raise EscrowReleaseNotAllowedError("escrow is disputed, only the agent can release funds.")
            return

        # Non-disputed case - check expiration
        gdpo = await self.world.node.api.database_api.get_dynamic_global_properties()
        now = gdpo.time
        expiration = escrow.escrow_expiration
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=UTC)

        is_expired = now >= expiration

        if not is_expired:
            # Before expiration: only cross-release allowed (sender→receiver, receiver→sender)
            if role == "sender" and receiver != escrow.to:
                raise EscrowReleaseNotAllowedError("before expiration, sender can only release to receiver.")
            if role == "receiver" and receiver != escrow.from_:
                raise EscrowReleaseNotAllowedError("before expiration, receiver can only release to sender.")
            if role == "agent":
                raise EscrowReleaseNotAllowedError("agent can only release after a dispute has been raised.")

    def _resolve_receiver(self) -> str:
        """
        Resolve the receiver of funds based on role.

        - sender releases to receiver (to)
        - receiver releases to sender (from_)
        - agent must specify receiver explicitly
        """
        # If receiver is explicitly provided, use it
        if self.receiver is not None:
            return self.receiver

        role = self.detected_role
        escrow = self.escrow_info

        # Auto-fill receiver based on role
        if role == "sender":
            return escrow.to  # sender releases to receiver
        if role == "receiver":
            return escrow.from_  # receiver releases to sender
        if role == "agent":
            # Agent must specify receiver explicitly
            raise EscrowAgentReceiverRequiredError

        raise ValueError(f"Unexpected role: {role}")  # pragma: no cover

    async def _create_operations(self) -> ComposeTransaction:
        yield EscrowReleaseOperation(
            from_=self.escrow_owner,
            to=self.escrow_info.to,
            agent=self.escrow_info.agent,
            who=self._role_to_who(),
            receiver=self.resolved_receiver,
            escrow_id=self.escrow_id,
            hbd_amount=self.hbd_amount,
            hive_amount=self.hive_amount,
        )
