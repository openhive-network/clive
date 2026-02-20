from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.update_transaction_metadata import UpdateTransactionMetadata
from clive.__private.core.constants.date import TRANSACTION_EXPIRATION_TIMEDELTA_DEFAULT
from clive.__private.core.ensure_transaction import TransactionConvertibleType, ensure_transaction
from clive.__private.core.iwax import WaxOperationFailedError
from clive.__private.models.schemas import HiveDateTime, HiveInt
from clive.__private.models.transaction import Transaction

if TYPE_CHECKING:
    from clive.__private.core.cached_offline_data import CachedTapos
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
    cached_tapos: CachedTapos | None = None

    async def _execute(self) -> None:
        transaction = ensure_transaction(self.content)
        try:
            iwax.validate_transaction(transaction)
        except WaxOperationFailedError as error:
            raise TransactionWaxValidationError(self, transaction, str(error)) from error

        if not transaction.is_tapos_set or self.force_update_metadata:
            if self.node is not None:
                await UpdateTransactionMetadata(
                    transaction=transaction, node=self.node, cached_tapos=self.cached_tapos
                ).execute()
            elif self.cached_tapos is not None:
                # Pure offline mode - no node at all, use cached TAPOS directly
                transaction.ref_block_num = HiveInt(self.cached_tapos.ref_block_num)
                transaction.ref_block_prefix = HiveInt(self.cached_tapos.ref_block_prefix)
                transaction.expiration = HiveDateTime(
                    self.cached_tapos.head_block_time + TRANSACTION_EXPIRATION_TIMEDELTA_DEFAULT
                )
            else:
                raise AssertionError("node or cached_tapos is required so that transaction metadata can be updated")

        self._result = transaction
