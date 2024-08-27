from __future__ import annotations

from datetime import timedelta
from typing import Any

from pydantic import Field, validator

from clive.__private.models.schemas import (
    HiveDateTime,
    HiveInt,
    OperationRepresentationUnion,
    OperationUnion,
    Signature,
    TransactionId,
    convert_to_representation,
)
from clive.__private.models.schemas import Transaction as SchemasTransaction


class Transaction(SchemasTransaction):
    operations: list[OperationRepresentationUnion] = Field(default_factory=list)
    ref_block_num: HiveInt = Field(default_factory=lambda: HiveInt(-1))
    ref_block_prefix: HiveInt = Field(default_factory=lambda: HiveInt(-1))
    expiration: HiveDateTime = Field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[Signature] = Field(default_factory=list)

    @property
    def operations_models(self) -> list[OperationUnion]:
        """Get only the operation models from already stored operations representations."""
        return [op.value for op in self.operations]  # type: ignore[attr-defined]

    @validator("operations", pre=True)
    @classmethod
    def convert_operations(cls, value: Any) -> list[OperationRepresentationUnion]:  # noqa: ANN401
        assert isinstance(value, list)
        return [convert_to_representation(op) for op in value]

    def add_operation(self, operation: OperationUnion) -> None:
        self.operations.append(convert_to_representation(operation))

    def is_signed(self) -> bool:
        return bool(self.signatures)

    def is_tapos_set(self) -> bool:
        return self.ref_block_num >= 0 and self.ref_block_prefix > 0

    def calculate_transaction_id(self) -> TransactionId:
        from clive.__private.core import iwax

        return TransactionId(iwax.calculate_transaction_id(self))

    def with_hash(self) -> TransactionWithHash:
        return TransactionWithHash(**self.dict(by_alias=True), transaction_id=self.calculate_transaction_id())


class TransactionWithHash(Transaction):
    transaction_id: TransactionId
