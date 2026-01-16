from __future__ import annotations

from typing import TYPE_CHECKING, Final, get_args

from clive.__private.core.commands.encrypt_memo import EncryptMemoKeyNotImportedError
from clive.__private.core.commands.encrypt_memo_with_account_names import AccountNotFoundForEncryptionError
from clive.__private.models.schemas import (
    TransferFromSavingsOperation,
    TransferOperation,
    TransferToSavingsOperation,
)
from clive.__private.ui.screens.operations.bindings.operation_action_bindings import OperationActionBindings

if TYPE_CHECKING:
    from clive.__private.models.schemas import OperationUnion

MEMO_KEY_NOT_IMPORTED_WARNING: Final[str] = "Memo encryption failed: memo key is not imported."

OperationWithMemo = TransferOperation | TransferToSavingsOperation | TransferFromSavingsOperation


class MemoEncryptingOperationActionBindings(OperationActionBindings):
    """
    Extension of OperationActionBindings that adds memo encryption support.

    Encrypts memos that start with '#' before adding operations to cart.
    If memo key is not imported, shows error notification and prevents the action.
    """

    _maybe_encrypted_operations: list[OperationUnion] | None = None

    def ensure_operations_list(self) -> list[OperationUnion]:
        """
        Return encrypted operations if available, otherwise delegate to parent.

        Returns:
            List of operations, possibly with encrypted memos.
        """
        if self._maybe_encrypted_operations is not None:
            return self._maybe_encrypted_operations
        return super().ensure_operations_list()

    async def _maybe_encrypt_memos_in_operations(self, operations: list[OperationUnion]) -> list[OperationUnion] | None:
        """
        Encrypt memos in operations that start with '#'.

        Args:
            operations: List of operations to process.

        Returns:
            List of operations with encrypted memos, or None if encryption failed.
        """
        result: list[OperationUnion] = []

        for operation in operations:
            if isinstance(operation, get_args(OperationWithMemo)):
                if operation.memo.startswith("#"):
                    encrypted_operation = await self._encrypt_memo_in_operation(operation)
                    if encrypted_operation is None:
                        return None
                    result.append(encrypted_operation)
                else:
                    result.append(operation)
            else:
                result.append(operation)

        return result

    async def _encrypt_memo_in_operation(self, operation: OperationWithMemo) -> OperationWithMemo | None:
        """
        Encrypt the memo in a single operation.

        Args:
            operation: The operation with memo to encrypt.

        Returns:
            The operation with encrypted memo, or None if encryption failed.
        """
        try:
            encrypted_memo_result = await self.commands.encrypt_memo_with_account_names(
                content=operation.memo,
                from_account=operation.from_,
                to_account=operation.to,
            )
            encrypted_memo = encrypted_memo_result.result_or_raise
        except EncryptMemoKeyNotImportedError:
            self.notify(MEMO_KEY_NOT_IMPORTED_WARNING, severity="error")
            return None
        except AccountNotFoundForEncryptionError as error:
            self.notify(f"Memo encryption failed: account '{error.account_name}' was not found.", severity="error")
            return None

        # Create a new operation instance with the encrypted memo
        if isinstance(operation, TransferFromSavingsOperation):
            return TransferFromSavingsOperation(
                from_=operation.from_,
                to=operation.to,
                amount=operation.amount,
                memo=encrypted_memo,
                request_id=operation.request_id,
            )
        if isinstance(operation, TransferToSavingsOperation):
            return TransferToSavingsOperation(
                from_=operation.from_,
                to=operation.to,
                amount=operation.amount,
                memo=encrypted_memo,
            )
        # TransferOperation
        return TransferOperation(
            from_=operation.from_,
            to=operation.to,
            amount=operation.amount,
            memo=encrypted_memo,
        )

    async def _handle_add_to_cart_request(self) -> None:
        """Handle add to cart request with memo encryption support."""
        operations = super().ensure_operations_list()
        if not operations:
            return

        # Encrypt memos if they start with '#'
        maybe_encrypted_operations = await self._maybe_encrypt_memos_in_operations(operations)
        if maybe_encrypted_operations is None:
            return

        self._maybe_encrypted_operations = maybe_encrypted_operations
        try:
            await super()._handle_add_to_cart_request()
        finally:
            self._maybe_encrypted_operations = None

    async def _handle_finalize_transaction_request(self) -> None:
        """Handle finalize transaction request with memo encryption support."""
        operations = super().ensure_operations_list()
        if not operations:
            return

        # Encrypt memos if they start with '#'
        maybe_encrypted_operations = await self._maybe_encrypt_memos_in_operations(operations)
        if maybe_encrypted_operations is None:
            return

        self._maybe_encrypted_operations = maybe_encrypted_operations
        try:
            await super()._handle_finalize_transaction_request()
        finally:
            self._maybe_encrypted_operations = None
