from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import ClassVar, TypeAlias

from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import Transaction
from clive.__private.storage.migrations import v0


class TransactionStorageModel(CliveBaseModel):
    transaction_core: Transaction
    transaction_file_path: Path | None = None


class ProfileStorageModel(v0.ProfileStorageModel):
    transaction: TransactionStorageModel | None  # type: ignore[assignment]  # changed storage model

    TransactionStorageModel: ClassVar[TypeAlias] = TransactionStorageModel

    @staticmethod
    def upgrade(old: v0.ProfileStorageModel) -> ProfileStorageModel:
        transaction = (
            TransactionStorageModel(
                transaction_core=Transaction(
                    ref_block_num=old.transaction.transaction_core.ref_block_num,
                    ref_block_prefix=old.transaction.transaction_core.ref_block_prefix,
                    expiration=old.transaction.transaction_core.expiration,
                    extensions=old.transaction.transaction_core.extensions,
                    signatures=old.transaction.transaction_core.signatures,
                    operations=old.transaction.transaction_core.operations,
                ),
                transaction_file_path=old.transaction.transaction_file_path,
            )
            if old.transaction
            else None
        )
        return ProfileStorageModel(
            name=old.name,
            working_account=old.working_account,
            tracked_accounts=old.tracked_accounts,
            known_accounts=old.known_accounts,
            key_aliases=old.key_aliases,
            transaction=transaction,
            chain_id=old.chain_id,
            node_address=old.node_address,
        )
