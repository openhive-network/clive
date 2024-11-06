from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from collections.abc import Iterator


class Transaction(SchemasTransaction):
    operations: list[OperationRepresentationUnion] = Field(default_factory=list)
    ref_block_num: HiveInt = Field(default_factory=lambda: HiveInt(-1))
    ref_block_prefix: HiveInt = Field(default_factory=lambda: HiveInt(-1))
    expiration: HiveDateTime = Field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[Signature] = Field(default_factory=list)

    def __bool__(self) -> bool:
        """Return True when there are any operations."""
        return bool(self.operations)

    def __contains__(self, operation: OperationRepresentationUnion | OperationUnion) -> bool:
        if isinstance(operation, OperationUnion):
            return operation in self.operations_models
        return operation in self.operations

    def __iter__(self) -> Iterator[OperationUnion]:  # type: ignore[override]
        return iter(self.operations_models)

    def __len__(self) -> int:
        return len(self.operations)

    @property
    def operations_models(self) -> list[OperationUnion]:
        """Get only the operation models from already stored operations representations."""
        return [op.value for op in self.operations]  # type: ignore[attr-defined]

    @validator("operations", pre=True)
    @classmethod
    def convert_operations(cls, value: Any) -> list[OperationRepresentationUnion]:  # noqa: ANN401
        assert isinstance(value, Iterable)
        return [convert_to_representation(op) for op in value]

    def add_operation(self, *operations: OperationUnion) -> None:
        operation_representations = self.convert_operations(operations)
        self.operations.extend(operation_representations)

    def remove_operation(self, *operations: OperationUnion) -> None:
        for op in self.operations:
            if op.value in operations:  # type: ignore[attr-defined]
                self.operations.remove(op)
                return

    def is_signed(self) -> bool:
        return bool(self.signatures)

    def is_tapos_set(self) -> bool:
        return self.ref_block_num >= 0 and self.ref_block_prefix > 0

    def calculate_transaction_id(self) -> TransactionId:
        from clive.__private.core import iwax

        return TransactionId(iwax.calculate_transaction_id(self))

    def reset(self) -> None:
        self.operations = []
        self.ref_block_num = HiveInt(-1)
        self.ref_block_prefix = HiveInt(-1)
        self.expiration = HiveDateTime.now() + timedelta(minutes=30)
        self.extensions = []
        self.signatures = []

    def swap_operations(self, index_1: int, index_2: int) -> None:
        self.operations[index_1], self.operations[index_2] = self.operations[index_2], self.operations[index_1]

    def with_hash(self) -> TransactionWithHash:
        return TransactionWithHash(**self.dict(by_alias=True), transaction_id=self.calculate_transaction_id())


class TransactionWithHash(Transaction):
    transaction_id: TransactionId
