from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
from pathlib import Path  # noqa: TCH003
from typing import Any, Sequence

from pydantic import Field

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers  # noqa: TCH001
from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    Signature,
)


class AlarmStorageModel(CliveBaseModel):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiers
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(CliveBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []


class KeyAliasStorageModel(CliveBaseModel):
    alias: str
    public_key: str


class TransactionCoreStorageModel(CliveBaseModel):
    operations: list[OperationRepresentationUnion] = Field(default_factory=list)
    ref_block_num: HiveInt = Field(default_factory=lambda: HiveInt(-1))
    ref_block_prefix: HiveInt = Field(default_factory=lambda: HiveInt(-1))
    expiration: HiveDateTime = Field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[Signature] = Field(default_factory=list)


class TransactionCoreStorageModelSchema(TransactionCoreStorageModel):
    operations: list[Any]
    """Do not include really complex structure of operation union type in the schema."""


class TransactionStorageModel(CliveBaseModel):
    transaction_core: TransactionCoreStorageModel
    transaction_file_path: Path | None = None


class TransactionStorageModelSchema(TransactionStorageModel):
    transaction_core: TransactionCoreStorageModelSchema


class ProfileStorageModel(CliveBaseModel):
    name: str
    working_account: str | None = None
    tracked_accounts: Sequence[TrackedAccountStorageModel] = []
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    transaction: TransactionStorageModel | None = None
    chain_id: str | None = None
    node_address: str


class PersistentStorageModel(CliveBaseModel):
    """Model used for serializing and deserializing the entire storage model."""

    default_profile: str | None = None
    profiles: list[ProfileStorageModel] = []  # noqa: RUF012


class AlarmStorageModelSchema(AlarmStorageModel):
    identifier: Any
    """Do not include alarm identifiers union in the schema so new alarms can be added without revision change."""


class TrackedAccountStorageModelSchema(TrackedAccountStorageModel):
    alarms: list[AlarmStorageModelSchema] = []  # noqa: RUF012


class ProfileStorageModelSchema(ProfileStorageModel):
    transaction: TransactionStorageModelSchema
    tracked_accounts: list[TrackedAccountStorageModelSchema] = []  # noqa: RUF012


class PersistentStorageModelSchema(PersistentStorageModel):
    """Should be used for generating schema of the storage model that could be later used for revision calculation."""

    profiles: list[ProfileStorageModelSchema] = []  # type: ignore[assignment] # noqa: RUF012


def get_storage_model_schema_json() -> str:
    return PersistentStorageModelSchema.schema_json(indent=4)


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]
