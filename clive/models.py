from __future__ import annotations

import re
from datetime import timedelta
from typing import Any, ClassVar, Literal, TypeAlias

from pydantic import Field, validator

from schemas.__private.hive_fields_basic_schemas import (
    AssetHbdHF26,
    AssetHiveHF26,
    AssetVestsHF26,
    HiveDateTime,
    HiveInt,
)
from schemas.__private.hive_fields_custom_schemas import Signature as SchemasSignature
from schemas.__private.operations import Hf26OperationType, HF26OperationTypes, Hf26VirtualOperationType
from schemas.__private.preconfigured_base_model import Operation as SchemasBaseOperationType
from schemas.__private.preconfigured_base_model import VirtualOperation as SchemasBaseVirtualOperationType
from schemas.transaction_model.transaction import Hf26Transaction

Operation = Hf26OperationType
VirtualOperation = Hf26VirtualOperationType
OperationBaseClass = SchemasBaseOperationType
VirtualOperationBaseClass = SchemasBaseVirtualOperationType

Signature = SchemasSignature


class Transaction(Hf26Transaction):
    ref_block_num: HiveInt = Field(default_factory=lambda: HiveInt(0))
    ref_block_prefix: HiveInt = Field(default_factory=lambda: HiveInt(0))
    expiration: HiveDateTime = Field(default_factory=lambda: HiveDateTime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[Signature] = Field(default_factory=list)

    @validator("operations", pre=True)
    def convert_operations(cls, value: Any) -> list[Operation]:  # noqa: N805
        assert isinstance(value, list)
        return [cls.__convert_to_h26(op) for op in value]

    def add_operation(self, operation: Operation) -> None:
        self.operations.append(self.__convert_to_h26(operation))

    @classmethod
    def __convert_to_h26(cls, operation: Operation) -> Operation:
        op_name = operation.get_name()
        return HF26OperationTypes[op_name](type=op_name, value=operation)  # type: ignore[call-arg]

    def is_signed(self) -> bool:
        return bool(self.signatures)


class Asset:
    HIVE: ClassVar[TypeAlias] = AssetHiveHF26
    HBD: ClassVar[TypeAlias] = AssetHbdHF26
    VESTS: ClassVar[TypeAlias] = AssetVestsHF26
    ANY: ClassVar[TypeAlias] = HIVE | HBD | VESTS
    ALLOWED_SYMBOLS: ClassVar[TypeAlias] = Literal["HIVE", "TESTS", "HBD", "TBD", "VESTS"]

    @classmethod
    def hive(cls, amount: float) -> Asset.HIVE:
        return Asset.HIVE(amount=cls.float_to_nai_int(amount, Asset.HIVE))

    @classmethod
    def hbd(cls, amount: float) -> Asset.HBD:
        return Asset.HBD(amount=cls.float_to_nai_int(amount, Asset.HBD))

    @classmethod
    def vests(cls, amount: float) -> Asset.VESTS:
        return Asset.VESTS(amount=cls.float_to_nai_int(amount, Asset.VESTS))

    @classmethod
    def float_to_nai_int(cls, number: float, asset_type: type[Asset.ANY]) -> int:
        result = number * (10 ** asset_type.get_asset_information().precision)
        assert result == int(result), "invalid precision"
        return int(result)

    @classmethod
    def resolve_symbol(cls, symbol: ALLOWED_SYMBOLS) -> type[Asset.ANY]:
        match symbol:
            case ["HIVE", "TESTS"]:
                return Asset.HIVE
            case ["HBD", "TBD"]:
                return Asset.HBD
            case "VESTS":
                return Asset.VESTS  # type: ignore[no-any-return]
            case _:
                raise ValueError(f"Unknown asset type: '{symbol}'")

    @classmethod
    def from_legacy(cls, legacy: str) -> Asset.ANY:
        legacy_parsing_regex = re.compile(r"(\d+\.\d+) ([A-Z]+)")
        parsed = legacy_parsing_regex.match(legacy)
        assert parsed is not None
        amount = int(parsed.group(1).replace(".", ""))
        symbol: Asset.ALLOWED_SYMBOLS = parsed.group(2)
        return cls.resolve_symbol(symbol)(amount=amount)
