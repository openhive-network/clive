from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from hashlib import sha256
from pathlib import Path  # noqa: TC003
from typing import Any

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers  # noqa: TC001
from clive.__private.core.date_utils import utc_epoch
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
    operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
    ref_block_num: HiveInt = HiveInt(-1)
    ref_block_prefix: HiveInt = HiveInt(-1)
    expiration: HiveDateTime = utc_epoch()  # type: ignore[assignment]
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


class ProfileStorageModel(CliveBaseModel):
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
        return hash(self.json(indent=4))


class AlarmStorageModelSchema(AlarmStorageModel):
    identifier: Any
    """Do not include alarm identifiers union in the schema so new alarms can be added without revision change."""


class TrackedAccountStorageModelSchema(TrackedAccountStorageModel):
    alarms: list[AlarmStorageModelSchema] = []  # noqa: RUF012


class ProfileStorageModelSchema(ProfileStorageModel):
    transaction: TransactionStorageModelSchema
    tracked_accounts: list[TrackedAccountStorageModelSchema] = []  # noqa: RUF012


def get_storage_model_schema_json() -> str:
    return ProfileStorageModelSchema.schema_json(indent=4)


def calculate_storage_model_revision() -> str:
    return sha256(get_storage_model_schema_json().encode()).hexdigest()[:8]
