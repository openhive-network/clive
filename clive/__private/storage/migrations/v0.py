from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from pathlib import Path  # noqa: TC003
from typing import Any, ClassVar, Self, TypeAlias

from clive.__private.core.date_utils import utc_epoch
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    PreconfiguredBaseModel,
    Signature,
)
from clive.__private.storage.migrations.base import ProfileStorageBase


class AlarmStorageModelBase(PreconfiguredBaseModel, tag_field="name", kw_only=True):
    @classmethod
    def name(cls) -> str:
        return cls.__struct_config__.tag

    is_harmless: bool = True
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class DateTimeAlarmIdentifierStorageModel(PreconfiguredBaseModel):
    value: HiveDateTime


class RecoveryAccountWarningListedAlarmIdentifierStorageModel(PreconfiguredBaseModel):
    recovery_account: str


class RecoveryAccountWarningListedStorageModel(
    AlarmStorageModelBase, tag="recovery_account_warning_listed", kw_only=True
):
    identifier: RecoveryAccountWarningListedAlarmIdentifierStorageModel


class GovernanceVotingExpirationStorageModel(AlarmStorageModelBase, tag="governance_voting_expiration", kw_only=True):
    identifier: DateTimeAlarmIdentifierStorageModel


class GovernanceNoActiveVotesStorageModel(AlarmStorageModelBase, tag="governance_no_active_votes", kw_only=True):
    identifier: DateTimeAlarmIdentifierStorageModel


class DecliningVotingRightsInProgressStorageModel(
    AlarmStorageModelBase, tag="declining_voting_rights_in_progress", kw_only=True
):
    identifier: DateTimeAlarmIdentifierStorageModel


class ChangingRecoveryAccountInProgressStorageModel(
    AlarmStorageModelBase, tag="changing_recovery_account", kw_only=True
):
    identifier: DateTimeAlarmIdentifierStorageModel


AllAlarmStorageModel = (
    RecoveryAccountWarningListedStorageModel
    | GovernanceVotingExpirationStorageModel
    | GovernanceNoActiveVotesStorageModel
    | DecliningVotingRightsInProgressStorageModel
    | ChangingRecoveryAccountInProgressStorageModel
)


class TrackedAccountStorageModel(PreconfiguredBaseModel):
    name: str
    alarms: Sequence[AllAlarmStorageModel] = []


class KeyAliasStorageModel(PreconfiguredBaseModel):
    alias: str
    public_key: str


class TransactionCoreStorageModel(PreconfiguredBaseModel):
    operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
    ref_block_num: HiveInt = HiveInt(-1)
    ref_block_prefix: HiveInt = HiveInt(-1)
    expiration: HiveDateTime = utc_epoch()  # type: ignore[assignment]
    extensions: list[Any] = []  # noqa: RUF012
    signatures: list[Signature] = []  # noqa: RUF012

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update({"type": "object", "description": "This should not be included in revision calculation"})


class TransactionStorageModel(PreconfiguredBaseModel):
    transaction_core: TransactionCoreStorageModel
    transaction_file_path: Path | None = None


class ProfileStorageModel(ProfileStorageBase, kw_only=True):
    name: str
    working_account: str | None = None
    tracked_accounts: Sequence[TrackedAccountStorageModel] = []
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    transaction: TransactionStorageModel | None = None
    chain_id: str | None = None
    node_address: str
    should_enable_known_accounts: bool = True

    _AllAlarmStorageModel: ClassVar[TypeAlias] = AllAlarmStorageModel
    _TrackedAccountStorageModel: ClassVar[TypeAlias] = TrackedAccountStorageModel
    _KeyAliasStorageModel: ClassVar[TypeAlias] = KeyAliasStorageModel
    _TransactionCoreStorageModel: ClassVar[TypeAlias] = TransactionCoreStorageModel
    _TransactionStorageModel: ClassVar[TypeAlias] = TransactionStorageModel
    _DateTimeAlarmIdentifierStorageModel: ClassVar[TypeAlias] = DateTimeAlarmIdentifierStorageModel
    _RecoveryAccountWarningListedAlarmIdentifierStorageModel: ClassVar[TypeAlias] = (
        RecoveryAccountWarningListedAlarmIdentifierStorageModel
    )
    _RecoveryAccountWarningListedStorageModel: ClassVar[TypeAlias] = RecoveryAccountWarningListedStorageModel
    _GovernanceVotingExpirationStorageModel: ClassVar[TypeAlias] = GovernanceVotingExpirationStorageModel
    _GovernanceNoActiveVotesStorageModel: ClassVar[TypeAlias] = GovernanceNoActiveVotesStorageModel
    _DecliningVotingRightsInProgressStorageModel: ClassVar[TypeAlias] = DecliningVotingRightsInProgressStorageModel
    _ChangingRecoveryAccountInProgressStorageModel: ClassVar[TypeAlias] = ChangingRecoveryAccountInProgressStorageModel

    @classmethod
    def upgrade(cls, old: ProfileStorageBase) -> Self:
        raise NotImplementedError("Upgrade is not not possible for first revision.")
