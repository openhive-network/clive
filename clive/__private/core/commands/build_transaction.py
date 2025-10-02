from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.update_transaction_metadata import UpdateTransactionMetadata
from clive.__private.core.ensure_transaction import TransactionConvertibleType, ensure_transaction
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class BuildTransaction(CommandWithResult[Transaction]):
    content: TransactionConvertibleType
    force_update_metadata: bool = False
    node: Node | None = None
    """Required only if force_update_metadata is True or transaction tapos is not set."""

    async def _execute(self) -> None:
        transaction = ensure_transaction(self.content)

        if not transaction.is_tapos_set or self.force_update_metadata:
            assert self.node is not None, "node is required so that transaction metadata can be updated"
            await UpdateTransactionMetadata(transaction=transaction, node=self.node).execute()

        self._result = transaction
