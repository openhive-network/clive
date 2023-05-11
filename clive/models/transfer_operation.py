from __future__ import annotations

from clive.models.operation import Operation
from schemas.operations import TransferOperation as TransferOperationSchema


class TransferOperation(Operation, TransferOperationSchema):
    def get_name(self) -> str:
        return "transfer_operation"

    def pretty(self, *, separator: str = "\n") -> str:
        return separator.join((f"{self.to=}", f"{self.amount=}", f"{self.memo=}"))
