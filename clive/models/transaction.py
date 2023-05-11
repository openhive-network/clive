from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from clive.models.operation import Operation  # noqa: TCH001


class Transaction(BaseModel):
    operations: list[Operation]
    signatures: list[str] = Field(default_factory=list)
    ref_block_num: int = 0
    ref_block_prefix: int = 0
    expiration: datetime = Field(default_factory=lambda: datetime.now() + timedelta(minutes=30))
    extensions: list[Any] = Field(default_factory=list)
    transaction_id: str = ""

    class Config:
        json_encoders = {
            Operation: lambda obj: obj.json(by_alias=True),
        }

    @property
    def signed(self) -> bool:
        return bool(self.signatures)

    def swap_order(self, index1: int, index2: int) -> None:
        self.operations[index1], self.operations[index2] = self.operations[index2], self.operations[index1]
