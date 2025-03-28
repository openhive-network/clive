from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path  # noqa: TCH003
from typing import Any, Sequence

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers  # noqa: TCH001
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    Signature,
)
from clive.__private.storage.migrations.storage_base_model import StorageBaseModel


class AlarmStorageModel(StorageBaseModel):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiers
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(StorageBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []


class KeyAliasStorageModel(StorageBaseModel):
    alias: str
    public_key: str


class TransactionCoreStorageModel(StorageBaseModel):
    operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
    ref_block_num: HiveInt = HiveInt(-1)
    ref_block_prefix: HiveInt = HiveInt(-1)
    expiration: HiveDateTime = datetime.fromtimestamp(0, tz=timezone.utc)  # type: ignore[assignment]
    extensions: list[Any] = []  # noqa: RUF012
    signatures: list[Signature] = []  # noqa: RUF012


class TransactionCoreStorageModelSchema(TransactionCoreStorageModel):
    operations: list[Any]
    """Do not include really complex structure of operation union type in the schema."""


class TransactionStorageModel(StorageBaseModel):
    transaction_core: TransactionCoreStorageModel
    transaction_file_path: Path | None = None


class TransactionStorageModelSchema(TransactionStorageModel):
    transaction_core: TransactionCoreStorageModelSchema


class ProfileStorageModel(StorageBaseModel):
    name: str
    working_account: str | None = None
    tracked_accounts: Sequence[TrackedAccountStorageModel] = []
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    transaction: TransactionStorageModel | None = None
    chain_id: str | None = None
    node_address: str

    def __hash__(self) -> int:
        return hash(self.json(indent=4))


class ProfileStorageModelSchema(ProfileStorageModel):
    transaction: TransactionStorageModelSchema


def get_storage_model_schema_json() -> str:
    return ProfileStorageModelSchema.schema_json(indent=4)


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]
