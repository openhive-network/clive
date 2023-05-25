from __future__ import annotations

from clive.models.operation import Operation
from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26
from schemas.operations import TransferOperation as TransferOperationSchema


class TransferOperation(Operation, TransferOperationSchema[AssetHiveHF26, AssetHbdHF26]):
    def pretty(self, *, separator: str = "\n") -> str:
        return separator.join((f"{self.to=}", f"{self.amount=}", f"{self.memo=}"))
