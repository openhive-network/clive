from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import ClassVar, Self, TypeAlias

from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import Transaction
from clive.__private.storage.migrations import v0


class TransactionStorageModel(CliveBaseModel):
    transaction_core: Transaction
    transaction_file_path: Path | None = None


class ProfileStorageModel(v0.ProfileStorageModel):
    transaction: TransactionStorageModel | None  # type: ignore[assignment]  # changed storage model

    TransactionStorageModel: ClassVar[TypeAlias] = TransactionStorageModel

    @classmethod
    def upgrade(cls, old: v0.ProfileStorageModel) -> Self:
        old_transaction = old.transaction
        new_transaction = (
            TransactionStorageModel(
                transaction_core=Transaction(
                    **old_transaction.transaction_core.dict(),
                ),
                transaction_file_path=old_transaction.transaction_file_path,
            )
            if old_transaction is not None
            else None
        )

        old_dict = old.dict()
        old_dict.pop("transaction")
        return cls(
            **old_dict,
            transaction=new_transaction,
        )
