"""
Chaining interface implementation for Clive SI.

This module implements a fluent API with method chaining for blockchain operations.
The interface is organized into groups of commands that can be called in sequence:

1. Main commands (e.g., transfer, transaction, update_authority)
2. Sub-commands (optional, command-specific, e.g., add_key for update_authority)
3. Process chaining (.process property) - allows adding multiple operations to a single transaction
4. Signing/Finalizing commands (autosign, sign_with, broadcast, save_file, as_transaction_object)

Key features:
- Groups can be called in flexible order
- Sub-commands (group 2) are specific to each main command and cannot be used with others
- Use .process to add another operation to the same transaction
- Finalizing commands can be called directly from main commands or after sub-commands
- Multiple operations are bundled into a single transaction when finalized

Example:
    double_transfer = await clive.process.transfer(
        from_account="alice",
        to_account="gtg",
        amount="1.000 HIVE",
        memo="Test transfer",
    ).process.transfer(
        from_account="alice",
        to_account="bob",
        amount="2.000 HIVE",
        memo="Test transfer2",
    ).sign_with(key="STM5...").as_transaction_object()
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self

from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save_transaction import SaveTransaction
from clive.__private.core.constants.transaction import DEFAULT_SERIALIZATION_MODE
from clive.__private.core.world import World
from clive.__private.models.transaction import Transaction
from clive.__private.si.core.process.process import (
    AuthorityBuilder,
    MultipleOperationsBuilder,
    OperationBuilder,
)

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.core.types import AuthorityLevelRegular, SerializationMode
    from clive.__private.core.world import World
    from clive.__private.si.process import ChainingOperationsInterface


async def broadcast_transaction(
    node: Node,
    transaction: Transaction,
) -> None:
    """Broadcast the transaction to the blockchain."""
    await Broadcast(node=node, transaction=transaction).execute()


async def save_transaction_to_file(
    transaction: Transaction,
    file_path: str | Path,
    file_format: Literal["json", "bin"] | None = None,
    serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE,
) -> None:
    """Save the transaction to a file."""
    await SaveTransaction(
        transaction=transaction,
        file_path=Path(file_path),
        force_format=file_format,
        serialization_mode=serialization_mode,
    ).execute()


class TransactionResult(Transaction):
    """
    Transaction result with convenience methods for broadcasting and saving.

    This class extends the base Transaction with additional methods that allow
    direct broadcasting to the blockchain or saving to a file without needing
    to go through the full command infrastructure.
    """

    def __str__(self) -> str:
        return self.json()

    async def broadcast(self) -> None:
        """Broadcast the transaction to the blockchain."""
        await broadcast_transaction(node=self._get_world().node, transaction=self)

    async def save_file(
        self,
        path: str | Path,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE,
    ) -> None:
        """Save the transaction to a file."""
        await save_transaction_to_file(
            transaction=self, file_path=Path(path), file_format=file_format, serialization_mode=serialization_mode
        )

    def _get_world(self) -> World:
        raise NotImplementedError


class ChainError(Exception):
    """Base exception for chaining interface errors."""


class ChainInvalidSubcommandError(ChainError):
    """Raised when a sub-command is used with incompatible main command."""


class TransactionFinalizer:
    """
    Base class providing transaction finalization methods.

    This mixin provides common methods for finalizing operations:
    - broadcast(): Sign and broadcast to blockchain
    - save_file(): Sign and save to file
    - as_transaction_object(): Get signed transaction object

    Subclasses must implement _get_signing_configuration() to provide
    signing keys and autosign preferences.
    """

    # These attributes are provided by subclasses
    world: World
    _current_operation: OperationBuilder | None
    _all_operations: list[OperationBuilder]

    def __init__(self, world: World, all_operations: list[OperationBuilder]) -> None:
        self.world = world
        self._all_operations = all_operations

    async def broadcast(self) -> None:
        """Broadcast the transaction to the blockchain."""
        sign_with, autosign = self._get_signing_configuration()
        await self._build_and_execute_transaction(
            world=self.world,
            builders=self._all_operations,
            sign_with=sign_with,
            save_file=None,
            broadcast=True,
            autosign=autosign,
        )

    async def save_file(
        self,
        path: str | Path,
        file_format: Literal["json", "bin"] = "json",
        serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE,
    ) -> None:
        """Save the transaction to a file."""
        sign_with, autosign = self._get_signing_configuration()
        await self._build_and_execute_transaction(
            world=self.world,
            builders=self._all_operations,
            sign_with=sign_with,
            save_file=path,
            file_format=file_format,
            serialization_mode=serialization_mode,
            broadcast=False,
            autosign=autosign,
        )

    async def as_transaction_object(self) -> TransactionResult:
        """Get the transaction without broadcasting or saving."""
        sign_with, autosign = self._get_signing_configuration()
        transaction = await self._build_and_execute_transaction(
            world=self.world,
            builders=self._all_operations,
            sign_with=sign_with,
            save_file=None,
            broadcast=False,
            autosign=autosign,
        )
        return create_transaction_result_class(world=self.world)(**transaction.dict())

    def _get_signing_configuration(self) -> tuple[list[str], bool]:
        """Return (signing_keys, autosign_flag) for transaction finalization."""
        return [], False

    async def _build_and_execute_transaction(  # noqa: PLR0913
        self,
        world: World,
        builders: list[OperationBuilder],
        sign_with: list[str],
        save_file: str | Path | None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE,
        *,
        broadcast: bool,
        autosign: bool,
    ) -> Transaction:
        """
        Build transaction from operation builders and execute requested actions.

        Handles both single and multiple operations, automatically choosing the
        appropriate finalization strategy. For multiple operations, combines them
        into a single transaction.

        Args:
            world: World instance providing blockchain context
            builders: List of OperationBuilder instances to process
            sign_with: List of key aliases to sign with (if any)
            save_file: File path to save to (if any)
            file_format: File format for saving (json or bin)
            serialization_mode: Serialization mode (legacy or hf26)
            broadcast: Whether to broadcast to blockchain
            autosign: Whether to automatically sign with available keys

        Returns:
            Finalized transaction
        """
        if len(builders) == 1:
            # Single operation - use existing run method
            return await builders[0].run(
                sign_with=sign_with,
                save_file=save_file,
                broadcast=broadcast,
                autosign=autosign,
                file_format=file_format,
                serialization_mode=serialization_mode,
            )
        # Multiple operations - combine into single transaction

        multi_builder = MultipleOperationsBuilder(
            world=world,
            builders=builders,
        )
        return await multi_builder.run(
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
            file_format=file_format,
            serialization_mode=serialization_mode,
        )


class ChainableOperationBuilder(TransactionFinalizer):
    """
    Represents a chain of blockchain operations being built.

    This class manages:
    - Previously built operations from earlier chain steps
    - The current operation being configured
    - Access to finalization methods (broadcast, save_file, as_transaction_object)
    - Access to the .process property for adding more operations
    - Access to signing configuration (sign_with, autosign)

    The chain pattern allows fluent API like:
        await clive.process.transfer(...).process.transfer(...).broadcast()
    """

    def __init__(self, world: World, previous_operations: list[OperationBuilder] | None = None) -> None:
        self._previous_operations = previous_operations or []
        self._current_operation: OperationBuilder | None = None
        super().__init__(world, all_operations=[])  # Will be provided via property

    @property
    def _all_operations(self) -> list[OperationBuilder]:
        """Get all operations including previous operations and current operation being built."""
        if self._current_operation is None:
            return self._previous_operations
        return [*self._previous_operations, self._current_operation]

    @_all_operations.setter
    def _all_operations(self, value: list[OperationBuilder]) -> None:
        """Setter required by parent class but not used."""
        # This setter exists only to satisfy parent class requirements
        # The actual value is computed dynamically via the getter

    @property
    def process(self) -> ChainingOperationsInterface:
        """Return interface to add another operation to the chain."""
        from clive.__private.si.process import ChainingOperationsInterface  # noqa: PLC0415

        assert self._current_operation is not None, "Operation must be set before chaining"

        return ChainingOperationsInterface(world=self.world, all_operations=self._all_operations)

    def sign_with(self, key: str) -> SigningChain:
        """Configure transaction to be signed with specific key. Can be chained for multiple signatures."""
        return SigningChain(self.world, self._all_operations, sign_keys=[key])

    def autosign(self) -> AutoSignChain:
        """Configure transaction to be auto-signed. Does NOT allow chaining with sign_with()."""
        return AutoSignChain(self.world, self._all_operations)


def create_transaction_result_class(world: World) -> type[TransactionResult]:
    """Factory function that creates a TransactionResult class with world context."""

    class TransactionResultImplementation(TransactionResult):
        def _get_world(self) -> World:
            return world

    return TransactionResultImplementation


class SigningChain(TransactionFinalizer):
    """
    Chain for configuring transaction signing with specific keys.

    Allows multiple sign_with() calls to add multiple signing keys.
    Each call adds another key to the list of keys that will be used
    to sign the transaction when finalized.
    """

    def __init__(
        self,
        world: World,
        all_operations: list[OperationBuilder],
        sign_keys: list[str],
    ) -> None:
        super().__init__(world, all_operations)
        self._sign_keys = sign_keys

    def sign_with(self, key: str) -> Self:
        """Add another key to sign the transaction with."""
        self._sign_keys.append(key)
        return self

    def _get_signing_configuration(self) -> tuple[list[str], bool]:
        """Provide signing parameters for multiple keys."""
        return self._sign_keys, False


class AutoSignChain(TransactionFinalizer):
    """
    Chain for automatic transaction signing.

    Uses automatic signing - the system will determine and use the appropriate
    keys from the profile. Does NOT allow manual sign_with() calls.
    """

    def _get_signing_configuration(self) -> tuple[list[str], bool]:
        """Provide signing parameters for autosign."""
        return [], True


class AuthorityUpdateChain(ChainableOperationBuilder):
    """
    Chain interface for building authority update operations.

    Provides methods to modify account authorities (owner, active, posting):
    - add_key / remove_key / modify_key: Manage key-based authorities
    - add_account / remove_account / modify_account: Manage account-based authorities

    All modifications are queued and applied when the transaction is finalized.
    """

    def __init__(
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int | None,
        previous_operations: list[OperationBuilder] | None = None,
    ) -> None:
        super().__init__(world, previous_operations)
        self._authority_type = authority_type
        self._account_name = account_name
        self._threshold = threshold
        self._current_operation = self._create_authority_builder()

    def add_key(self, *, key: str, weight: int) -> Self:
        """
        Schedule adding a key to the authority.

        Args:
            key: Public key to add (e.g., 'STM5...' or alias from key manager)
            weight: Weight/voting power for this key (typically 1)

        Returns:
            Self for method chaining
        """
        self._get_authority_builder().add_key(key=key, weight=weight)
        return self

    def add_account(self, *, account_name: str, weight: int) -> Self:
        """
        Schedule adding an account to the authority.

        Args:
            account_name: Account name to add
            weight: Weight/voting power for this account

        Returns:
            Self for method chaining
        """
        self._get_authority_builder().add_account(account_name=account_name, weight=weight)
        return self

    def remove_key(self, *, key: str) -> Self:
        """
        Schedule removing a key from the authority.

        Args:
            key: Public key to remove

        Returns:
            Self for method chaining
        """
        self._get_authority_builder().remove_key(key=key)
        return self

    def remove_account(self, *, account_name: str) -> Self:
        """
        Schedule removing an account from the authority.

        Args:
            account_name: Account name to remove

        Returns:
            Self for method chaining
        """
        self._get_authority_builder().remove_account(account_name=account_name)
        return self

    def modify_key(self, *, key: str, weight: int) -> Self:
        """
        Schedule modifying a key's weight in the authority.

        Args:
            key: Public key to modify
            weight: New weight for this key

        Returns:
            Self for method chaining
        """
        self._get_authority_builder().modify_key(key=key, weight=weight)
        return self

    def modify_account(self, *, account: str, weight: int) -> Self:
        """
        Schedule modifying an account's weight in the authority.

        Args:
            account: Account name to modify
            weight: New weight for this account

        Returns:
            Self for method chaining
        """
        self._get_authority_builder().modify_account(account=account, weight=weight)
        return self

    def _create_authority_builder(self) -> AuthorityBuilder:
        """Create AuthorityBuilder instance for this authority update."""
        return AuthorityBuilder(
            world=self.world,
            authority_type=self._authority_type,
            account_name=self._account_name,
            threshold=self._threshold,
        )

    def _get_authority_builder(self) -> AuthorityBuilder:
        """Get the AuthorityBuilder instance, ensuring type safety."""
        assert isinstance(self._current_operation, AuthorityBuilder), "Current operation must be AuthorityBuilder"
        return self._current_operation
