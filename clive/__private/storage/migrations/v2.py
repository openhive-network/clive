from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

from pydantic import validator

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers  # noqa: TCH001
from clive.__private.logger import logger
from clive.__private.models.schemas import Transaction  # noqa: TCH001
from clive.__private.storage.migrations.storage_base_model import StorageBaseModel


class AlarmStorageModel(StorageBaseModel):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiers
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(StorageBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []

    @validator("alarms", pre=True, always=True)
    def validate_alarms(cls, value: list[Any]) -> Sequence[AlarmStorageModel]:  # noqa: N805
        try:
            return [AlarmStorageModel.parse_obj(entry) for entry in value]
        except (ValueError, TypeError):
            logger.warning("Failed to parse alarms loaded from file")
            return []


class KeyAliasStorageModel(StorageBaseModel):
    alias: str
    public_key: str


class TransactionStorageModel(StorageBaseModel):
    schemas_transaction: Transaction
    transaction_file_path: Path | None = None


class TransactionStorageModelSchema(TransactionStorageModel):
    schemas_transaction: Any


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

    @validator("transaction", pre=True, always=True)
    def validate_transaction(cls, value: object) -> TransactionStorageModel | None:  # noqa: N805
        try:
            return TransactionStorageModel.parse_obj(value) if value is not None else None
        except (ValueError, TypeError):
            logger.warning("Failed to parse transaction loaded from file")
            return None


class ProfileStorageModelSchema(ProfileStorageModel):
    transaction: TransactionStorageModelSchema


def get_storage_model_schema_json() -> str:
    return ProfileStorageModelSchema.schema_json(indent=4)


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]


def get_storage_version() -> str:
    return Path(__file__).stem
