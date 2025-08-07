from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from pathlib import Path  # noqa: TC003
from typing import Any, Self

from clive.__private.core.alarms.specific_alarms import (
    ChangingRecoveryAccountInProgress,
    DecliningVotingRightsInProgress,
    GovernanceNoActiveVotes,
    GovernanceVotingExpiration,
    RecoveryAccountWarningListed,
)
from clive.__private.core.date_utils import utc_epoch
from clive.__private.models.schemas import (
    HiveDateTime,
    OperationRepresentationUnion,
    PreconfiguredBaseModel,
    Signature,
    Uint16t,
    Uint32t,
    field,
)
from clive.__private.storage.migrations.base import ProfileStorageBase


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

    class DateTimeAlarmIdentifierStorageModel(PreconfiguredBaseModel):
        value: HiveDateTime

    class RecoveryAccountWarningListedAlarmIdentifierStorageModel(PreconfiguredBaseModel):
        recovery_account: str

    type AllAlarmIdentifiersStorageModel = (
        DateTimeAlarmIdentifierStorageModel | RecoveryAccountWarningListedAlarmIdentifierStorageModel
    )

    class AlarmStorageModelBase(PreconfiguredBaseModel, tag_field="name", kw_only=True):
        @classmethod
        def get_name(cls) -> str:
            assert isinstance(cls.__struct_config__.tag, str), "Alarm storage models must have a string tag."
            return cls.__struct_config__.tag

        is_harmless: bool = True
        """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""

    class RecoveryAccountWarningListedStorageModel(
        AlarmStorageModelBase, tag=RecoveryAccountWarningListed.get_name(), kw_only=True
    ):
        identifier: ProfileStorageModel.RecoveryAccountWarningListedAlarmIdentifierStorageModel

    class GovernanceVotingExpirationStorageModel(
        AlarmStorageModelBase, tag=GovernanceVotingExpiration.get_name(), kw_only=True
    ):
        identifier: ProfileStorageModel.DateTimeAlarmIdentifierStorageModel

    class GovernanceNoActiveVotesStorageModel(
        AlarmStorageModelBase, tag=GovernanceNoActiveVotes.get_name(), kw_only=True
    ):
        identifier: ProfileStorageModel.DateTimeAlarmIdentifierStorageModel

    class DecliningVotingRightsInProgressStorageModel(
        AlarmStorageModelBase, tag=DecliningVotingRightsInProgress.get_name(), kw_only=True
    ):
        identifier: ProfileStorageModel.DateTimeAlarmIdentifierStorageModel

    class ChangingRecoveryAccountInProgressStorageModel(
        AlarmStorageModelBase, tag=ChangingRecoveryAccountInProgress.get_name(), kw_only=True
    ):
        identifier: ProfileStorageModel.DateTimeAlarmIdentifierStorageModel

    type AllAlarmStorageModel = (
        RecoveryAccountWarningListedStorageModel
        | GovernanceVotingExpirationStorageModel
        | GovernanceNoActiveVotesStorageModel
        | DecliningVotingRightsInProgressStorageModel
        | ChangingRecoveryAccountInProgressStorageModel
    )

    class TrackedAccountStorageModel(PreconfiguredBaseModel):
        name: str
        alarms: Sequence[ProfileStorageModel.AllAlarmStorageModel] = []

    class KeyAliasStorageModel(PreconfiguredBaseModel):
        alias: str
        public_key: str

    class TransactionCoreStorageModel(PreconfiguredBaseModel):
        operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
        ref_block_num: Uint16t = 0
        ref_block_prefix: Uint32t = 0
        expiration: HiveDateTime = field(default_factory=lambda: HiveDateTime(utc_epoch()))
        extensions: list[Any] = []  # noqa: RUF012
        signatures: list[Signature] = []  # noqa: RUF012

    class TransactionStorageModel(PreconfiguredBaseModel):
        transaction_core: ProfileStorageModel.TransactionCoreStorageModel
        transaction_file_path: Path | None = None

    @classmethod
    def upgrade(cls, old: ProfileStorageBase) -> Self:
        raise NotImplementedError("Upgrade is not not possible for first revision.")
