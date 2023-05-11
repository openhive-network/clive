from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from clive.models.operation import Operation  # noqa: TCH001


class Transaction(BaseModel):
    operations: list[Operation]
    ref_block_num: int = 0
    ref_block_prefix: int = 0
    expiration: datetime = Field(default_factory=lambda: datetime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    signatures: list[str] | None = None

    @property
    def signed(self) -> bool:
        return bool(self.signatures)

    def swap_order(self, index1: int, index2: int) -> None:
        self.operations[index1], self.operations[index2] = self.operations[index2], self.operations[index1]

    def as_json(self, by_alias: bool = True, exclude_none: bool = True) -> str:
        class OperationWrapper(BaseModel):
            value: Operation
            type_: str = Field(alias="type")

        obj = self.copy(deep=True)
        obj.operations = [OperationWrapper(value=op, type=op.get_name()) for op in obj.operations]  # type: ignore
        return obj.json(by_alias=by_alias, exclude_none=exclude_none)
