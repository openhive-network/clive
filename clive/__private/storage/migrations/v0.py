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
from clive.__private.storage.migrations.base import AlarmStorageModelBase, ProfileStorageBase
from schemas._exclude_json_schema_toolset import TreeExclusion, merge_excluded_fields_for_schema_dictionaries


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

    @classmethod
    def _excluded_fields_for_schema_json(cls) -> TreeExclusion:
        return merge_excluded_fields_for_schema_dictionaries(
            super()._excluded_fields_for_schema_json(),
            {
                "transaction": {
                    "transaction_core": {"operations": None},
                }
            },
        )

    class DateTimeAlarmIdentifierStorageModel(PreconfiguredBaseModel):
        value: HiveDateTime

    class RecoveryAccountWarningListedAlarmIdentifierStorageModel(PreconfiguredBaseModel):
        recovery_account: str

    AllAlarmIdentifiersStorageModel = (
        DateTimeAlarmIdentifierStorageModel | RecoveryAccountWarningListedAlarmIdentifierStorageModel
    )

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

    AllAlarmStorageModel = (
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

    @classmethod
    def _preprocess_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        cls._ensure_non_negative_tapos_fields(data)
        return data

    @staticmethod
    def _ensure_non_negative_tapos_fields(data: dict[str, Any]) -> None:
        """
        Ensure that specific TAPoS fields in the transaction data are non-negative.

        This method modifies the data loaded from a disk to ensure that the specified TAPoS
        fields, namely 'ref_block_num' and 'ref_block_prefix' within the transaction, are non-negative.
        If the fields are absent or their values are negative, they are set to `0`.

        This method exists because in previous versions of storage we included `-1`
        by default.

        Args:
            data: The profile storage data stored on the disk.
        """
        transaction: dict[str, Any] | None = data.get("transaction", {})
        if transaction is None:
            # transaction can be also none, so we skip in that case
            return

        transaction_core = transaction.get("transaction_core", {})
        for field_ in ("ref_block_num", "ref_block_prefix"):
            value = transaction_core.get(field_, 0)
            transaction_core[field_] = max(value, 0)
