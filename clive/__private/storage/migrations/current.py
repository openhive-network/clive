from __future__ import annotations

from typing import Final

from clive.__private.storage.migrations.v2 import (
    AlarmStorageModel,
    KeyAliasStorageModel,
    ProfileStorageModel,
    ProfileStorageModelSchema,
    TrackedAccountStorageModel,
    TransactionStorageModel,
    calculate_storage_model_revision,
    get_storage_model_schema_json,
    get_storage_version,
)

__all__ = [
    "AlarmStorageModel",
    "KeyAliasStorageModel",
    "ProfileStorageModel",
    "ProfileStorageModelSchema",
    "TrackedAccountStorageModel",
    "TransactionStorageModel",
    "calculate_storage_model_revision",
    "get_storage_model_schema_json",
    "get_storage_version",
]

FIRST_VERSION: Final[str] = "c600278a"


def get_storage_version_list() -> list[str]:
    current_revision = get_storage_version()
    num = int(current_revision[1:])
    revision_list = [f"v{i}" for i in range(1, num + 1)]
    revision_list.insert(0, FIRST_VERSION)
    return revision_list


def compare_versions(a: str, b: str) -> int:
    return get_storage_version_list().index(a) - get_storage_version_list().index(b)
