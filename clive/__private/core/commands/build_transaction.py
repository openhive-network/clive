from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.update_transaction_metadata import UpdateTransactionMetadata
from clive.__private.core.ensure_transaction import TransactionConvertibleType, ensure_transaction
from clive.models import Transaction

if TYPE_CHECKING:
    from clive.__private.core.node import Node


@dataclass(kw_only=True)
class BuildTransaction(CommandWithResult[Transaction]):
    DEFAULT_UPDATE_METADATA: ClassVar[bool] = False

    content: TransactionConvertibleType
    update_metadata: bool = DEFAULT_UPDATE_METADATA
    node: Node | None = None
    """Required only if update_metadata is True."""

    async def _execute(self) -> None:
        transaction = ensure_transaction(self.content)

        if self.update_metadata:
            assert self.node is not None, "node is required when update_metadata is True"
            await UpdateTransactionMetadata(transaction=transaction, node=self.node).execute()

        self._result = transaction
