from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.update_transaction_metadata import UpdateTransactionMetadata
from clive.__private.core.ensure_transaction import TransactionConvertibleType, ensure_transaction
from clive.__private.core.iwax import WaxOperationFailedError
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.__private.core.node import Node


class TransactionWaxValidationError(CommandError):
    def __init__(self, command: BuildTransaction, transaction: Transaction, wax_error_details: str) -> None:
        self.transaction = transaction
        self.wax_error_details = wax_error_details

        reason = f"Transaction validation failed.\nWax error details:\n{wax_error_details}"
        super().__init__(command, reason)


@dataclass(kw_only=True)
class BuildTransaction(CommandWithResult[Transaction]):
    content: TransactionConvertibleType
    force_update_metadata: bool = False
    node: Node | None = None
    """Required only if force_update_metadata is True or transaction tapos is not set."""

    async def _execute(self) -> None:
        transaction = ensure_transaction(self.content)
        try:
            iwax.validate_transaction(transaction)
        except WaxOperationFailedError as error:
            raise TransactionWaxValidationError(self, transaction, str(error)) from error

        if not transaction.is_tapos_set or self.force_update_metadata:
            assert self.node is not None, "node is required so that transaction metadata can be updated"
            await UpdateTransactionMetadata(transaction=transaction, node=self.node).execute()

        self._result = transaction
