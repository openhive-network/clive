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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self

from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.save_transaction import SaveTransaction
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.world import World
from clive.__private.models.transaction import Transaction
from clive.__private.si.core.process.process import (
    ProcessAuthority,
    ProcessCommandBase,
    ProcessCustomJson,
    ProcessMultipleOperations,
    ProcessPowerDownCancel,
    ProcessPowerDownRestart,
    ProcessPowerDownStart,
    ProcessPowerUp,
    ProcessTransaction,
    ProcessTransfer,
)

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.si.process import ProcessInterfaceBase


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
    serialization_mode: Literal["legacy", "hf26"] | None = None,
) -> None:
    """Save the transaction to a file."""
    await SaveTransaction(
        transaction=transaction,
        file_path=Path(file_path),
        force_format=file_format,
        serialization_mode=serialization_mode,
    ).execute()


#######################################################################################################################################


class GetTransactionResult(Transaction):
    """Result after getting a transaction."""

    def _get_world(self) -> World:
        raise NotImplementedError

    async def broadcast(self) -> None:
        """Broadcast the transaction to the blockchain."""
        await broadcast_transaction(node=self._get_world().node, transaction=self)

    async def save_file(
        self,
        path: str | Path,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: Literal["legacy", "hf26"] | None = None,
    ) -> None:
        """Save the transaction to a file."""
        await save_transaction_to_file(
            transaction=self, file_path=Path(path), file_format=file_format, serialization_mode=serialization_mode
        )


###############################################################################
if TYPE_CHECKING:
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.asset import Asset


class ChainError(Exception):
    """Base exception for chaining interface errors."""


class ChainSequenceError(ChainError):
    """Raised when chaining sequence is violated."""


class ChainDuplicateCallError(ChainError):
    """Raised when a group is called more than once (except sub-commands)."""


class ChainInvalidSubcommandError(ChainError):
    """Raised when a sub-command is used with incompatible main command."""


class _FinalizingBase:
    """Base class for finalizing chains - contains common finalization methods."""

    # These attributes are provided by BaseChain
    world: World
    _operation_builder: ProcessCommandBase | None
    _operation_builders: list[ProcessCommandBase]

    def __init__(self, world: World, operation_builders: list[ProcessCommandBase]) -> None:
        self.world = world
        self._operation_builders = operation_builders

    def _get_sign_params(self) -> tuple[list[str], bool]:
        return [], False

    async def broadcast(self) -> None:
        """Broadcast the transaction to the blockchain."""
        sign_with, autosign = self._get_sign_params()
        await self._finalize_operation_builders(
            world=self.world,
            operation_builders=self._operation_builders,
            sign_with=sign_with,
            save_file=None,
            broadcast=True,
            autosign=autosign,
        )

    async def save_file(
        self,
        path: str | Path,
        file_format: Literal["json", "bin"] = "json",
        serialization_mode: Literal["legacy", "hf26"] = "hf26",
    ) -> None:
        """Save the transaction to a file."""
        sign_with, autosign = self._get_sign_params()
        await self._finalize_operation_builders(
            world=self.world,
            operation_builders=self._operation_builders,
            sign_with=sign_with,
            save_file=path,
            file_format=file_format,
            serialization_mode=serialization_mode,
            broadcast=False,
            autosign=autosign,
        )

    async def as_transaction_object(self) -> GetTransactionResult:
        """Get the transaction without broadcasting or saving."""
        sign_with, autosign = self._get_sign_params()
        transaction = await self._finalize_operation_builders(
            world=self.world,
            operation_builders=self._operation_builders,
            sign_with=sign_with,
            save_file=None,
            broadcast=False,
            autosign=autosign,
        )
        return as_transaction_object_result_cls(world=self.world)(**transaction.dict())

    async def _finalize_operation_builders(  # noqa: PLR0913
        self,
        world: World,
        operation_builders: list[ProcessCommandBase],
        sign_with: list[str],
        save_file: str | Path | None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: Literal["legacy", "hf26"] | None = None,
        *,
        broadcast: bool,
        autosign: bool,
    ) -> Transaction:
        """Helper function to finalize single or multiple operation builders.

        Args:
            world: World instance
            operation_builders: List of ProcessCommandBase instances that build operations
            sign_with: List of aliases of keys to sign with (if any)
            save_file: File path to save to (if any)
            file_format: File format for saving (json or bin)
            serialization_mode: Serialization mode (legacy or hf26)
            broadcast: Whether to broadcast
            autosign: Whether to auto-sign

        Returns:
            Finalized transaction
        """
        if len(operation_builders) == 1:
            # Single operation - use existing finalize method
            return await operation_builders[0].finalize(
                sign_with=sign_with,
                save_file=save_file,
                broadcast=broadcast,
                autosign=autosign,
                file_format=file_format,
                serialization_mode=serialization_mode,
            )
        # Multiple operations - create operations and combine

        multi_processor = ProcessMultipleOperations(
            world=world,
            operation_builders=operation_builders,
        )
        return await multi_processor.finalize(
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
            file_format=file_format,
            serialization_mode=serialization_mode,
        )


class BaseChain(_FinalizingBase):
    """Base class for all chaining interfaces."""

    def __init__(self, world: World, operation_builders: list[ProcessCommandBase] | None = None) -> None:
        super().__init__(world, operation_builders or [])
        self._operation_builder: ProcessCommandBase | None = None
        self.main_command_type: str | None = None

    def _create_processor(self) -> ProcessCommandBase:
        """Create the appropriate operation builder for this chain."""

    def _get_all_operation_builders(self) -> list[ProcessCommandBase]:
        """Get all operation builders including existing operations and current operation builder."""
        assert self._operation_builder is not None, "Operation builder must be set before finalizing"
        return [*self._operation_builders, self._operation_builder]

    @property
    def process(self) -> ProcessInterfaceBase:
        """Return ProcessInterface to add another operation to the chain."""
        from clive.__private.si.process import ProcessInterfaceChaining  # noqa: PLC0415

        assert self._operation_builder is not None, "Operation builder must be set before chaining"

        return ProcessInterfaceChaining(
            world=self.world, operation_builders=[*self._operation_builders, self._operation_builder]
        )

    def sign_with(self, key: str) -> SignWithChain:
        """Configure transaction to be signed with specific key. Can be chained for multiple signatures."""
        return SignWithChain(self.world, self._get_all_operation_builders(), sign_keys=[key])

    def autosign(self) -> AutoSignChain:
        """Configure transaction to be auto-signed. Does NOT allow chaining with sign_with()."""
        return AutoSignChain(self.world, self._get_all_operation_builders())


def as_transaction_object_result_cls(world: World) -> type[GetTransactionResult]:
    class GetTransactionResultImplementation(GetTransactionResult):
        def _get_world(self) -> World:
            return world

    return GetTransactionResultImplementation


class SignWithChain(_FinalizingBase):
    """Handles sign_with chaining - allows multiple sign_with() calls."""

    def __init__(
        self,
        world: World,
        operation_builders: list[ProcessCommandBase],
        sign_keys: list[str],
    ) -> None:
        super().__init__(world, operation_builders)
        self._sign_keys = sign_keys

    def sign_with(self, key: str) -> Self:
        """Add another key to sign the transaction with."""
        self._sign_keys.append(key)
        return self

    def _get_sign_params(self) -> tuple[list[str], bool]:
        """Provide signing parameters for multiple keys."""
        return self._sign_keys, False


class AutoSignChain(_FinalizingBase):
    """Handles autosign - does NOT allow sign_with() calls."""

    def _get_sign_params(self) -> tuple[list[str], bool]:
        """Provide signing parameters for autosign."""
        return [], True


class AuthorityChain(BaseChain):
    """Chain interface for authority update operations."""

    def __init__(
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int,
        operation_builders: list[ProcessCommandBase] | None = None,
    ) -> None:
        super().__init__(world, operation_builders)
        self.main_command_type = "authority"
        self._authority_type = authority_type
        self._account_name = account_name
        self._threshold = threshold
        self._operation_builder = self._create_processor()

    def _create_processor(self) -> ProcessAuthority:
        """Create ProcessAuthority instance."""
        return ProcessAuthority(
            world=self.world,
            authority_type=self._authority_type,
            account_name=self._account_name,
            threshold=self._threshold,
        )

    def add_key(self, *, key: str, weight: int) -> Self:
        """Add a key to the authority (sub-command)."""
        self._validate_sub_command()
        assert isinstance(self._operation_builder, ProcessAuthority), "Operation builder must be ProcessAuthority"
        self._operation_builder.add_key(key=key, weight=weight)
        return self

    def add_account(self, *, account_name: str, weight: int) -> Self:
        """Add an account to the authority (sub-command)."""
        self._validate_sub_command()
        assert isinstance(self._operation_builder, ProcessAuthority), "Operation builder must be ProcessAuthority"
        self._operation_builder.add_account(account_name=account_name, weight=weight)
        return self

    def remove_key(self, *, key: str) -> Self:
        """Remove a key from the authority (sub-command)."""
        self._validate_sub_command()
        assert isinstance(self._operation_builder, ProcessAuthority), "Operation builder must be ProcessAuthority"
        self._operation_builder.remove_key(key=key)
        return self

    def remove_account(self, *, account_name: str) -> Self:
        """Remove an account from the authority (sub-command)."""
        self._validate_sub_command()
        assert isinstance(self._operation_builder, ProcessAuthority), "Operation builder must be ProcessAuthority"
        self._operation_builder.remove_account(account_name=account_name)
        return self

    def modify_key(self, *, key: str, weight: int) -> Self:
        """Modify a key in the authority (sub-command)."""
        self._validate_sub_command()
        assert isinstance(self._operation_builder, ProcessAuthority), "Operation builder must be ProcessAuthority"
        self._operation_builder.modify_key(key=key, weight=weight)
        return self

    def modify_account(self, *, account: str, weight: int) -> Self:
        """Modify an account in the authority (sub-command)."""
        self._validate_sub_command()
        assert isinstance(self._operation_builder, ProcessAuthority), "Operation builder must be ProcessAuthority"
        self._operation_builder.modify_account(account=account, weight=weight)
        return self

    def _validate_sub_command(self) -> None:
        """Validate that sub-commands can be called."""
        if self.main_command_type != "authority":
            raise ChainInvalidSubcommandError("Authority sub-commands can only be used with authority operations")

