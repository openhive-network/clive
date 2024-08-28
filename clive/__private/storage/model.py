from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from hashlib import sha256
from typing import Any

from pydantic import Field

from clive.__private.core.alarms.alarm_identifier import AlarmIdentifier  # noqa: TCH001
from clive.__private.core.types import AuthoritiesT  # noqa: TCH001
from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import OperationRepresentationUnion  # noqa: TCH001


class AlarmStorageModel(CliveBaseModel):
    name: str
    is_harmless: bool = False
    identifier: AlarmIdentifier
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class KeyAliasStorageModel(CliveBaseModel):
    alias: str
    public_key: str


class KeyAliasStorageModel(CliveBaseModel):
    alias: str
    public_key: str


class AccountAuthorityStorageModel(CliveBaseModel):
    account: str
    role: str
    # key_weights: set[KeyWeight] = field(default_factory=set)
    # authority_weights: set[AuthorityWeight] = field(default_factory=set)
    required_total_weight: int


class AuthoritiesStorageModel(CliveBaseModel):
    authorities: set[AccountAuthorityStorageModel] = Field(default_factory=set)
    authorities_lut: set[AccountAuthorityStorageModel] = Field(default_factory=set)
    last_updated: datetime


class TrackedAccountStorageModel(CliveBaseModel):
    name: str
    alarms: list[AlarmStorageModel] = []  # noqa: RUF012
    authorities: AuthorityesStorageModel | None = None


class KeyAliasStorageModel(CliveBaseModel):
    alias: str
    public_key: str


class ProfileStorageModel(CliveBaseModel):
    name: str
    working_account: str | None = None
    tracked_accounts: list[TrackedAccountStorageModel] = []  # noqa: RUF012
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    cart_operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
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
