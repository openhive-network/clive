from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

import msgspec

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers  # noqa: TCH001
from clive.__private.core.date_utils import utc_epoch
from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    Signature,
)


class AlarmStorageModel(CliveBaseModel, kw_only=True):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiers
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(CliveBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []


class KeyAliasStorageModel(CliveBaseModel, kw_only=True):
    alias: str
    public_key: str


class TransactionCoreStorageModel(CliveBaseModel):
    operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
    ref_block_num: HiveInt = msgspec.field(default=-1)
    ref_block_prefix: HiveInt = msgspec.field(default=-1)
    expiration: HiveDateTime = msgspec.field(default=utc_epoch().__str__())  # type: ignore[assignment]
    extensions: list[Any] = []  # noqa: RUF012
    signatures: list[Signature] = []  # noqa: RUF012


class TransactionCoreStorageModelSchema(TransactionCoreStorageModel):
    operations: list[Any]
    """Do not include really complex structure of operation union type in the schema."""


class TransactionStorageModel(CliveBaseModel):
    transaction_core: TransactionCoreStorageModel
    transaction_file_path: Path | None = None


class TransactionStorageModelSchema(TransactionStorageModel):
    transaction_core: TransactionCoreStorageModelSchema


class ProfileStorageModel(CliveBaseModel, kw_only=True):
    name: str
    working_account: str | None = None
    tracked_accounts: Sequence[TrackedAccountStorageModel] = []
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    transaction: TransactionStorageModel | None = None
    chain_id: str | None = None
    node_address: str


class AlarmStorageModelSchema(AlarmStorageModel, kw_only=True):
    identifier: Any
    """Do not include alarm identifiers union in the schema so new alarms can be added without revision change."""


class TrackedAccountStorageModelSchema(TrackedAccountStorageModel, kw_only=True):
    alarms: list[AlarmStorageModelSchema] = []  # noqa: RUF012


class ProfileStorageModelSchema(ProfileStorageModel, kw_only=True):
    transaction: TransactionStorageModelSchema
    tracked_accounts: list[TrackedAccountStorageModelSchema] = []  # noqa: RUF012

    @classmethod
    def schema_json(cls) -> str:
        schema = msgspec.json.schema(cls, schema_hook=schema_hook)
        return msgspec.json.encode(schema)


def schema_hook(obj: Any) -> dict:
    if obj is Path:
        return {"type": "string", "format": "path"}
    if obj is HiveInt:
        return {"type": "integer"}
    if obj is HiveDateTime:
        return {"type": "string", "format": "date-time"}
    raise NotImplementedError(f"Objects of type {obj} are not supported")


def get_storage_model_schema_json() -> str:
    return ProfileStorageModelSchema.schema_json()


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json()).hexdigest()[:8]
