from __future__ import annotations

from hashlib import sha256
from pathlib import Path  # noqa: TCH003
from typing import Any, Sequence

import msgspec

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers  # noqa: TCH001
from clive.__private.core.date_utils import utc_epoch
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    PreconfiguredBaseModel,
    Signature,
)


class AlarmStorageModel(PreconfiguredBaseModel, kw_only=True):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiers
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(PreconfiguredBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []


class KeyAliasStorageModel(PreconfiguredBaseModel, kw_only=True):
    alias: str
    public_key: str


class TransactionCoreStorageModel(PreconfiguredBaseModel):
    operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
    ref_block_num: HiveInt = msgspec.field(default=-1)
    ref_block_prefix: HiveInt = msgspec.field(default=-1)
    expiration: HiveDateTime = msgspec.field(default=utc_epoch().__str__())  # type: ignore[assignment]
    extensions: list[Any] = []  # noqa: RUF012
    signatures: list[Signature] = []  # noqa: RUF012


class TransactionCoreStorageModelSchema(TransactionCoreStorageModel):
    operations: list[Any]
    """Do not include really complex structure of operation union type in the schema."""


class TransactionStorageModel(PreconfiguredBaseModel):
    transaction_core: TransactionCoreStorageModel
    transaction_file_path: Path | None = None


class TransactionStorageModelSchema(TransactionStorageModel):
    transaction_core: TransactionCoreStorageModelSchema


class ProfileStorageModel(PreconfiguredBaseModel, kw_only=True):
    name: str
    working_account: str | None = None
    tracked_accounts: Sequence[TrackedAccountStorageModel] = []
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    transaction: TransactionStorageModel | None = None
    chain_id: str | None = None
    node_address: str
    should_enable_known_accounts: bool = True

    def __hash__(self) -> int:
        return hash(self.json())


class AlarmStorageModelSchema(AlarmStorageModel, kw_only=True):
    identifier: Any
    """Do not include alarm identifiers union in the schema so new alarms can be added without revision change."""


class TrackedAccountStorageModelSchema(TrackedAccountStorageModel, kw_only=True):
    alarms: list[AlarmStorageModelSchema] = []  # noqa: RUF012


class ProfileStorageModelSchema(ProfileStorageModel, kw_only=True):
    transaction: TransactionStorageModelSchema
    tracked_accounts: list[TrackedAccountStorageModelSchema] = []  # noqa: RUF012


def get_storage_model_schema_json() -> str:
    return ProfileStorageModelSchema.schema_json()


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]
