from __future__ import annotations

from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, cast

from clive.__private.core.commands.load_transaction import LoadTransaction
from clive.__private.core.constants.transaction import DEFAULT_SERIALIZATION_MODE
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.core.keys.keys import PublicKey
from clive.__private.core.operations.transfer_operations import create_transfer_operation
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import TransferOperation
from clive.__private.models.transaction import Transaction
from clive.__private.si.core.base import CommandBase
from clive.__private.si.core.process import authority_operations
from clive.__private.si.exceptions import MissingFromFileOrFromObjectError
from clive.__private.si.validators import (
    AlreadySignedModeValidator,
    LoadTransactionFromFileFromObjectValidator,
    SignedTransactionValidator,
)
from clive.__private.validators.path_validator import PathValidator

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular, SerializationMode
    from clive.__private.core.world import World
    from clive.__private.models.schemas import AccountUpdate2Operation, Authority, OperationUnion


class OperationBuilder(CommandBase[Transaction], ABC):
    """
    Abstract base class for building individual blockchain operations.

    Each builder is responsible for:
    1. Storing operation parameters (e.g., from_account, to_account for transfers)
    2. Validating the configuration before execution
    3. Creating the actual blockchain operation (TransferOperation, etc.)
    4. Managing finalization parameters (signing keys, broadcast flags, save paths)

    Concrete implementations include:
    - TransferBuilder: builds transfer operations
    - TransactionBuilder: loads and processes existing transactions
    - AuthorityBuilder: builds authority update operations
    - MultipleOperationsBuilder: combines multiple operations into one transaction
    """

    def __init__(self, world: World) -> None:
        super().__init__()
        self.world = world
        self._sign_with: str | None = None
        self._save_file: str | Path | None = None
        self._broadcast: bool = False
        self._autosign: bool | None = None

    async def _run(self) -> Transaction:
        """Not used - OperationBuilder uses run() with parameters instead."""
        raise NotImplementedError("OperationBuilder uses run() with parameters, not _run()")

    async def run(  # noqa: PLR0913
        self,
        sign_with: list[str] | str | None = None,
        save_file: str | Path | None = None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
        force_unsign: bool | None = None,
        already_signed_mode: AlreadySignedMode | None = None,
    ) -> Transaction:
        """Execute the operation with specified signing and broadcasting options."""
        sign_keys = self._normalize_sign_with(sign_with)

        # Set instance variables so they're available in _get_transaction_content()
        self._sign_with = (
            sign_with[0]
            if isinstance(sign_with, list) and sign_with
            else sign_with
            if isinstance(sign_with, str)
            else None
        )
        self._save_file = save_file
        self._broadcast = broadcast
        self._autosign = autosign

        await self.validate()
        content = await self._get_transaction_content()

        # Normalize sign_keys to the format expected by perform_actions_on_transaction
        normalized_sign_keys: PublicKey | list[PublicKey] | None = None
        if sign_keys:
            normalized_sign_keys = sign_keys[0] if len(sign_keys) == 1 else sign_keys

        kwargs: dict[str, Any] = {
            "content": content,
            "sign_keys": normalized_sign_keys,
            "autosign": bool(autosign),
            "save_file_path": Path(save_file) if save_file else None,
            "force_save_format": file_format,
            "serialization_mode": serialization_mode,
            "broadcast": broadcast,
        }
        if force_unsign is not None:
            kwargs["force_unsign"] = force_unsign
        if already_signed_mode is not None:
            kwargs["already_signed_mode"] = already_signed_mode

        return (await self.world.commands.perform_actions_on_transaction(**kwargs)).result_or_raise

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """Get the operation to be processed."""

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return await self._create_operation()

    def _resolve_key_or_alias(self, key_or_alias: str) -> PublicKey:
        """
        Resolve a key or alias to a PublicKey.

        Args:
            key_or_alias: Either a public key string or an alias to a key in the key manager.

        Returns:
            PublicKey instance.

        Raises:
            KeyNotFoundError: If the alias is not found in the key manager.
        """
        try:
            aliased_key = self.world.profile.keys.get_from_alias(key_or_alias)
            return PublicKey(value=aliased_key.value)
        except KeyNotFoundError:
            return PublicKey(value=key_or_alias)

    def _normalize_sign_with(self, sign_with: list[str] | str | None) -> list[PublicKey]:
        """Normalize sign_with parameter to a list of PublicKey objects."""
        if isinstance(sign_with, str):
            sign_keys_or_aliases = [sign_with]
        elif isinstance(sign_with, list):
            sign_keys_or_aliases = sign_with
        else:
            sign_keys_or_aliases = []

        return [self._resolve_key_or_alias(key_or_alias) for key_or_alias in sign_keys_or_aliases]


class TransferBuilder(OperationBuilder):
    """Builds transfer operations for sending HIVE or HBD between accounts."""

    def __init__(
        self,
        world: World,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> None:
        super().__init__(world)
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.memo = memo

    async def _create_operation(self) -> TransferOperation:
        return create_transfer_operation(
            from_account=self.from_account,
            to_account=self.to_account,
            amount=self.amount,
            memo=self.memo,
        )


class TransactionBuilder(OperationBuilder):
    """
    Builds operations by loading an existing transaction from file or object.

    This builder handles both signed and unsigned transactions, with options for
    force-unsigning and controlling already-signed transaction behavior.
    """

    def __init__(  # noqa: PLR0913
        self,
        world: World,
        already_signed_mode: AlreadySignedMode | None,
        from_file: str | Path | None,
        from_object: Transaction | None = None,
        *,
        force_unsign: bool,
        force: bool,
    ) -> None:
        super().__init__(world)
        self.from_file = from_file
        self.from_object = from_object
        self.force_unsign = force_unsign
        self.already_signed_mode = already_signed_mode
        self.force = force

    async def validate(self) -> None:
        LoadTransactionFromFileFromObjectValidator(
            from_file=self.from_file,
            from_object=self.from_object,
        ).validate()
        if self.already_signed_mode is not None:
            AlreadySignedModeValidator(
                use_autosign=self._autosign,
                already_signed_mode=self.already_signed_mode,
            ).validate()
            transaction = await self._get_transaction_content()
            if transaction.is_signed:
                SignedTransactionValidator(
                    sign_with=self._sign_with,
                    already_signed_mode=self.already_signed_mode,
                ).validate()
            if self.from_file is not None:
                PathValidator(mode="is_file").validate(
                    value=str(self.from_file),
                )

    async def run(  # noqa: PLR0913
        self,
        sign_with: list[str] | str | None = None,
        save_file: str | Path | None = None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
        force_unsign: bool | None = None,
        already_signed_mode: AlreadySignedMode | None = None,
    ) -> Transaction:
        """Execute the operation with specified signing and broadcasting options."""
        # Use instance values if parameters not provided
        return await super().run(
            sign_with=sign_with,
            save_file=save_file,
            file_format=file_format,
            serialization_mode=serialization_mode,
            broadcast=broadcast,
            autosign=autosign,
            force_unsign=force_unsign if force_unsign is not None else self.force_unsign,
            already_signed_mode=already_signed_mode if already_signed_mode is not None else self.already_signed_mode,
        )

    async def _create_operation(self) -> OperationUnion:
        """TransactionBuilder uses _get_transaction_content() instead."""
        raise NotImplementedError("TransactionBuilder uses _get_transaction_content() instead of _create_operation")

    async def _get_transaction_content(self) -> Transaction:
        if self.from_file is not None:
            return await LoadTransaction(
                file_path=self.from_file if isinstance(self.from_file, Path) else Path(self.from_file)
            ).execute_with_result()
        if self.from_object is not None:
            return self.from_object
        raise MissingFromFileOrFromObjectError


class AuthorityBuilder(OperationBuilder):
    """
    Builds authority update operations by managing callbacks that modify authority structures.

    This builder uses a callback pattern to queue modifications (add_key, remove_account, etc.)
    that are applied when the operation is finalized. This allows chaining multiple
    modifications before creating the final AccountUpdate2Operation.
    """

    def __init__(
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int | None = None,
    ) -> None:
        super().__init__(world)
        self.authority_type = authority_type
        self.account_name = account_name
        self.threshold = threshold
        self._callbacks: list[Callable[[Authority], Authority]] = []
        # Add threshold callback only if threshold is provided
        if threshold is not None:
            self._callbacks.append(partial(authority_operations.set_threshold, threshold=threshold))

    def add_key(self, *, key: str, weight: int) -> Self:
        """Add a key with specified weight to the authority."""
        self._callbacks.append(partial(authority_operations.add_key, key=key, weight=weight))
        return self

    def add_account(self, *, account_name: str, weight: int) -> Self:
        """Add an account with specified weight to the authority."""
        self._callbacks.append(partial(authority_operations.add_account, account=account_name, weight=weight))
        return self

    def remove_key(self, *, key: str) -> Self:
        """Remove a key from the authority."""
        self._callbacks.append(partial(authority_operations.remove_key, key=key))
        return self

    def remove_account(self, *, account_name: str) -> Self:
        """Remove an account from the authority."""
        self._callbacks.append(partial(authority_operations.remove_account, account=account_name))
        return self

    def modify_key(self, *, key: str, weight: int) -> Self:
        """Modify the weight of an existing key."""
        self._callbacks.append(partial(authority_operations.modify_key, key=key, weight=weight))
        return self

    def modify_account(self, *, account: str, weight: int) -> Self:
        """Modify the weight of an existing account."""
        self._callbacks.append(partial(authority_operations.modify_account, account=account, weight=weight))
        return self

    async def _create_operation(self) -> AccountUpdate2Operation:
        """Build the account_update2_operation by applying all callbacks."""
        # Fetch current account state
        accounts = (await self.world.commands.find_accounts(accounts=[self.account_name])).result_or_raise
        account = accounts[0]

        # Use authority_operations to build the operation
        return authority_operations.build_account_update_operation(
            account=account,
            authority_type=self.authority_type,
            callbacks=self._callbacks,
        )


class MultipleOperationsBuilder(OperationBuilder):
    """
    Combines multiple operation builders into a single transaction.

    This builder is used when chaining operations with .process property.
    It collects operations from all builders and merges them, preserving
    transaction metadata if one of the builders is a TransactionBuilder.
    """

    def __init__(
        self,
        world: World,
        builders: list[OperationBuilder],
    ) -> None:
        super().__init__(world)
        self.builders = builders

    async def validate(self) -> None:
        """Validate that signed transactions cannot have operations added to them."""
        from clive.__private.si.exceptions import CannotAddOperationToSignedTransactionError  # noqa: PLC0415

        # Check if any of the builders is a TransactionBuilder with a signed transaction
        for builder in self.builders:
            if isinstance(builder, TransactionBuilder):
                # Get the transaction from TransactionBuilder
                transaction_content = await builder._get_transaction_content()
                if transaction_content.is_signed and not builder.force_unsign:
                    raise CannotAddOperationToSignedTransactionError

        await super().validate()

    async def _create_operation(self) -> OperationUnion:
        """Not used for multiple operations - we override _get_transaction_content instead."""
        raise NotImplementedError("MultipleOperationsBuilder uses _get_transaction_content() instead")

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """Get all operations from all builders and preserve transaction metadata."""
        operations: list[OperationUnion] = []
        base_transaction: Transaction | None = None

        for builder in self.builders:
            # Get content from each builder
            content = await builder._get_transaction_content()
            # If content is already a Transaction (e.g., from TransactionBuilder), extract operations and metadata
            if isinstance(content, Transaction):
                # Store the first transaction we encounter to preserve its metadata
                if base_transaction is None:
                    base_transaction = content
                # Use operations_models to get OperationUnion objects instead of representations
                operations.extend(content.operations_models)
            # If content is a list of operations
            elif isinstance(content, list):
                operations.extend(content)
            # Single operation (from _create_operation)
            else:
                operation = cast("OperationUnion", content)  # required for type checker
                operations.append(operation)

        # If we found a base transaction, preserve its metadata
        if base_transaction is not None:
            # Create a new transaction with the combined operations but preserve metadata from base transaction
            return Transaction(
                operations=Transaction.convert_operations(operations),
                ref_block_num=base_transaction.ref_block_num,
                ref_block_prefix=base_transaction.ref_block_prefix,
                expiration=base_transaction.expiration,
                extensions=base_transaction.extensions,
                # Don't copy signatures - they will be invalid after adding operations
                signatures=[],
            )

        # If no base transaction, return list of operations (will be converted to transaction with default metadata)
        return operations
