from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from pathlib import Path  # noqa: TC003
from typing import Any, Self, TypeAlias

from clive.__private.core.date_utils import utc_epoch
from clive.__private.models.schemas import PreconfiguredBaseModel
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    Signature,
)
from clive.__private.storage.migrations.base import ProfileStorageBase


class DateTimeAlarmIdentifierStorageModel(PreconfiguredBaseModel):
    value: HiveDateTime


class RecoveryAccountWarningListedAlarmIdentifierStorageModel(PreconfiguredBaseModel):
    recovery_account: str


AllAlarmIdentifiersStorageModel = (
    DateTimeAlarmIdentifierStorageModel | RecoveryAccountWarningListedAlarmIdentifierStorageModel
)


class AlarmStorageModel(PreconfiguredBaseModel, kw_only=True):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiersStorageModel
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(PreconfiguredBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []


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

    _AlarmStorageModel: TypeAlias = AlarmStorageModel  # noqa: UP040
    _TrackedAccountStorageModel: TypeAlias = TrackedAccountStorageModel  # noqa: UP040
    _KeyAliasStorageModel: TypeAlias = KeyAliasStorageModel  # noqa: UP040
    _TransactionCoreStorageModel: TypeAlias = TransactionCoreStorageModel  # noqa: UP040
    _TransactionStorageModel: TypeAlias = TransactionStorageModel  # noqa: UP040
    _DateTimeAlarmIdentifierStorageModel: TypeAlias = DateTimeAlarmIdentifierStorageModel  # noqa: UP040
    _RecoveryAccountWarningListedAlarmIdentifierStorageModel: TypeAlias = (  # noqa: UP040
        RecoveryAccountWarningListedAlarmIdentifierStorageModel
    )
    _AllAlarmIdentifiersStorageModel: TypeAlias = AllAlarmIdentifiersStorageModel  # noqa: UP040

    @classmethod
    def upgrade(cls, old: ProfileStorageBase) -> Self:
        raise NotImplementedError("Upgrade is not not possible for first revision.")
