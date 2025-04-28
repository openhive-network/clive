from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Self

from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import Transaction as SchemasTransaction
from clive.__private.storage.migrations import v0


class _StorageDefinitions0(v0.StorageDefinitions):
    class Transaction(SchemasTransaction):
        __modify_schema__ = v0.StorageDefinitions.TransactionCoreStorageModel.__modify_schema__


class StorageDefinitions(_StorageDefinitions0):
    class TransactionStorageModel(CliveBaseModel):
        transaction_core: _StorageDefinitions0.Transaction
        transaction_file_path: Path | None = None


class ProfileStorageModel(v0.ProfileStorageModel):
    _REVISION_NONCE = 1

    transaction: StorageDefinitions.TransactionStorageModel | None = None  # type: ignore[assignment]  # changed storage model

    @classmethod
    def upgrade(cls, old: v0.ProfileStorageModel) -> Self:
        old_transaction = old.transaction
        new_transaction = (
            StorageDefinitions.TransactionStorageModel(
                transaction_core=StorageDefinitions.Transaction(
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
