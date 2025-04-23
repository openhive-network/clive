# noqa: I002
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar, TypeAlias

from clive.__private.core.alarms.all_identifiers import AllAlarmIdentifiers
from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    Signature,
)
from clive.__private.storage.migrations.base import ProfileStorageBase


class AlarmStorageModel(CliveBaseModel):
    name: str
    is_harmless: bool = False
    identifier: AllAlarmIdentifiers
    """Identifies the occurrence of specific alarm among other possible alarms of same type. E.g. end date."""


class TrackedAccountStorageModel(CliveBaseModel):
    name: str
    alarms: Sequence[AlarmStorageModel] = []


class TransactionCoreStorageModel(CliveBaseModel):
    operations: list[OperationRepresentationUnion] = []  # noqa: RUF012
    ref_block_num: HiveInt = HiveInt(-1)
    ref_block_prefix: HiveInt = HiveInt(-1)
    expiration: HiveDateTime = datetime.fromtimestamp(0, tz=UTC)  # type: ignore[assignment]
    extensions: list[Any] = []  # noqa: RUF012
    signatures: list[Signature] = []  # noqa: RUF012


class TransactionStorageModel(CliveBaseModel):
    transaction_core: TransactionCoreStorageModel
    transaction_file_path: Path | None = None


class ProfileStorageModel(ProfileStorageBase):
    class KeyAliasStorageModel(CliveBaseModel):
        alias: str
        public_key: str

    name: str
    working_account: str | None = None
    tracked_accounts: Sequence[TrackedAccountStorageModel] = []
    known_accounts: list[str] = []  # noqa: RUF012
    key_aliases: list[KeyAliasStorageModel] = []  # noqa: RUF012
    transaction: TransactionStorageModel | None = None
    chain_id: str | None = None
    node_address: str
    should_enable_known_accounts: bool = True

    AlarmStorageModel: ClassVar[TypeAlias] = AlarmStorageModel
    TrackedAccountStorageModel: ClassVar[TypeAlias] = TrackedAccountStorageModel
    TransactionCoreStorageModel: ClassVar[TypeAlias] = TransactionCoreStorageModel
    TransactionStorageModel: ClassVar[TypeAlias] = TransactionStorageModel
