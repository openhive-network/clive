from __future__ import annotations

from clive.models.operation import Operation
from schemas.operations import TransferOperation as TransferOperationSchema


class TransferOperation(Operation, TransferOperationSchema):
    def get_name(self) -> str:
        return "transfer"

    def pretty(self, *, separator: str = "\n") -> str:
        return f"to={self.to}{separator}amount={self.amount}{separator}memo={self.memo}"
