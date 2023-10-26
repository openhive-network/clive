from __future__ import annotations

from datetime import timedelta
from typing import Any

from pydantic import Field, validator

from clive.models import Operation, Signature  # noqa: TCH001
from clive.models.aliased import OperationRepresentationType  # noqa: TCH001
from schemas.fields.hex import TransactionId
from schemas.fields.hive_datetime import HiveDateTime
from schemas.fields.hive_int import HiveInt
from schemas.operations.representations import convert_to_representation
from schemas.transaction import Transaction as SchemasTransaction


class Transaction(SchemasTransaction):
    operations: list[OperationRepresentationType] = Field(default_factory=list)
    ref_block_num: HiveInt = Field(default_factory=lambda: HiveInt(0))
    ref_block_prefix: HiveInt = Field(default_factory=lambda: HiveInt(0))
    expiration: HiveDateTime = Field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[Signature] = Field(default_factory=list)

    @property
    def operations_models(self) -> list[Operation]:
        """Get only the operation models from already stored operations representations."""
        return [op.value for op in self.operations]  # type: ignore[attr-defined]

    @validator("operations", pre=True)
    @classmethod
    def convert_operations(cls, value: Any) -> list[OperationRepresentationType]:
        assert isinstance(value, list)
        return [convert_to_representation(op) for op in value]

    def add_operation(self, operation: Operation) -> None:
        self.operations.append(convert_to_representation(operation))

    def is_signed(self) -> bool:
        return bool(self.signatures)

    def calculate_transaction_id(self) -> TransactionId:
        from clive.__private.core import iwax

        return TransactionId(iwax.calculate_transaction_id(self))

    def with_hash(self) -> TransactionWithHash:
        # TODO: There is an issue with __convert_to_h26(), the type of `operation` is not Operation but could be Any.
        #  After resolving and making it to work with dict, it should be possible to **self.dict(by_alias=True)
        #  like: return TransactionWithHash(**self.dict(by_alias=True) , transaction_id=iwax.calculate_transaction_id(self))

        data = self.dict(by_alias=True)
        data["operations"] = self.operations.copy()

        return TransactionWithHash(**data, transaction_id=self.calculate_transaction_id())


class TransactionWithHash(Transaction):
    transaction_id: TransactionId
