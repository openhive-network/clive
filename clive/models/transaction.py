from __future__ import annotations

from datetime import timedelta
from typing import Any

from pydantic import Field, validator

from clive.__private.core import iwax
from clive.models import Operation, Signature  # noqa: TCH001
from schemas.__private.hive_fields_basic_schemas import HiveDateTime, HiveInt
from schemas.__private.hive_fields_custom_schemas import TransactionId  # noqa: TCH001
from schemas.__private.operations import Hf26OperationRepresentation, HF26OperationTypes
from schemas.transaction_model.transaction import Hf26Transaction


class Transaction(Hf26Transaction):
    operations: list[Hf26OperationRepresentation] = Field(default_factory=list)
    ref_block_num: HiveInt = Field(default_factory=lambda: HiveInt(0))
    ref_block_prefix: HiveInt = Field(default_factory=lambda: HiveInt(0))
    expiration: HiveDateTime = Field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[Signature] = Field(default_factory=list)

    @validator("operations", pre=True)
    @classmethod
    def convert_operations(cls, value: Any) -> list[Hf26OperationRepresentation]:
        assert isinstance(value, list)
        return [cls.__convert_to_h26(op) for op in value]

    def add_operation(self, operation: Operation) -> None:
        self.operations.append(self.__convert_to_h26(operation))

    @classmethod
    def __convert_to_h26(cls, operation: Any) -> Hf26OperationRepresentation:
        if isinstance(operation, Hf26OperationRepresentation):
            return operation
        op_name = operation.get_name()

        # Why is there `Hf26OperationType` type hint in the `HF26OperationTypes` structure when they re no longer of Operation type?
        return HF26OperationTypes[op_name](type=op_name, value=operation)  # type: ignore[call-arg, return-value]

    def is_signed(self) -> bool:
        return bool(self.signatures)

    def with_hash(self) -> TransactionWithHash:
        # TODO: There is an issue with __convert_to_h26(), the type of `operation` is not Operation but could be Any.
        #  After resolving and making it to work with dict, it should be possible to **self.dict(by_alias=True)
        #  like: return TransactionWithHash(**self.dict(by_alias=True) , transaction_id=iwax.calculate_transaction_id(self))

        data = self.dict(by_alias=True)
        data["operations"] = self.operations.copy()

        return TransactionWithHash(**data, transaction_id=iwax.calculate_transaction_id(self))


class TransactionWithHash(Transaction):
    transaction_id: TransactionId
