from __future__ import annotations

from hashlib import sha256
from typing import Any

from clive.__private.core.alarms.alarm_identifier import AlarmIdentifier  # noqa: TCH001
from clive.models import OperationRepresentationType  # noqa: TCH001
from clive.models.base import CliveBaseModel


class AlarmStorageModel(CliveBaseModel):
    name: str
    is_harmless: bool = False
    identifier: AlarmIdentifier
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class KnownAccountStorageModel(CliveBaseModel):
    name: str


class TrackedAccountStorageModel(CliveBaseModel):
    name: str
    alarms: list[AlarmStorageModel] = []  # noqa: RUF012


class KeyAliasStorageModel(CliveBaseModel):
    alias: str
    public_key: str


class ProfileStorageModel(CliveBaseModel):
    name: str
    working_account: str | None = None
    tracked_accounts: list[TrackedAccountStorageModel] = []  # noqa: RUF012
    known_accounts: list[KnownAccountStorageModel] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    cart_operations: list[OperationRepresentationType] = []  # noqa: RUF012
    chain_id: str | None = None
    node_address: str


class PersistentStorageModel(CliveBaseModel):
    """Model used for serializing and deserializing the entire storage model."""

    default_profile: str | None = None
    profiles: list[ProfileStorageModel] = []  # noqa: RUF012


class ProfileStorageModelSchema(ProfileStorageModel):
    cart_operations: list[Any] = []  # noqa: RUF012
    """Do not include really complex structure of operation union type in the schema."""


class PersistentStorageModelSchema(PersistentStorageModel):
    """Should be used for generating schema of the storage model that could be later used for revision calculation."""

    profiles: list[ProfileStorageModelSchema] = []  # type: ignore[assignment] # noqa: RUF012


def get_storage_model_schema_json() -> str:
    return PersistentStorageModelSchema.schema_json(indent=4)


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]
