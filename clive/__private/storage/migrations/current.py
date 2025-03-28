from __future__ import annotations

from clive.__private.storage.migrations.v1 import (
    AlarmStorageModel,
    KeyAliasStorageModel,
    TrackedAccountStorageModel,
)
from clive.__private.storage.migrations.v2 import (
    ProfileStorageModel,
    ProfileStorageModelSchema,
    TransactionStorageModel,
    calculate_storage_model_revision,
    get_storage_model_schema_json,
)
from clive.__private.storage.migrations.version import Version

__all__ = [
    "AlarmStorageModel",
    "KeyAliasStorageModel",
    "ProfileStorageModel",
    "ProfileStorageModelSchema",
    "TrackedAccountStorageModel",
    "TransactionStorageModel",
    "calculate_storage_model_revision",
    "get_storage_model_schema_json",
]


def get_storage_version() -> Version:
    return Version.V2
