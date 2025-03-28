from __future__ import annotations

from hashlib import sha256
from pathlib import Path  # noqa: TCH003
from typing import Any

from clive.__private.models.schemas import Transaction  # noqa: TCH001
from clive.__private.storage.migrations import v1
from clive.__private.storage.migrations.storage_base_model import StorageBaseModel


class TransactionStorageModel(StorageBaseModel):
    schemas_transaction: Transaction
    transaction_file_path: Path | None = None


class TransactionStorageModelSchema(TransactionStorageModel):
    schemas_transaction: Any


class ProfileStorageModel(v1.ProfileStorageModel):
    transaction: TransactionStorageModel | None = None  # type: ignore[assignment]


class ProfileStorageModelSchema(ProfileStorageModel):
    transaction: TransactionStorageModelSchema


def get_storage_model_schema_json() -> str:
    return ProfileStorageModelSchema.schema_json(indent=4)


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]
