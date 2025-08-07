from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Self

from clive.__private.models.schemas import PreconfiguredBaseModel, Transaction
from clive.__private.storage.migrations import v0


class ProfileStorageModel(v0.ProfileStorageModel):
    _REVISION_NONCE = 1

    transaction: TransactionStorageModel | None = None  # type: ignore[assignment]  # changed storage model

    class TransactionStorageModel(PreconfiguredBaseModel):
        transaction_core: Transaction
        transaction_file_path: Path | None = None

    @classmethod
    def upgrade(cls, old: v0.ProfileStorageModel) -> Self:  # type: ignore[override]  # should always take previous model
        old_transaction = old.transaction
        new_transaction = (
            ProfileStorageModel.TransactionStorageModel(
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
