from __future__ import annotations

from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, cast

from clive.__private.cli.commands.process.process_account_update import (
    ProcessAccountUpdate,
    add_account,
    add_key,
    modify_account,
    modify_key,
    remove_account,
    remove_key,
    set_threshold,
    update_authority,
)
from clive.__private.si.core.process.process_transaction import (
    ProcessTransaction as CLIProcessTransaction,
)
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.core.keys.keys import PublicKey
from clive.__private.models.asset import Asset
from clive.__private.models.transaction import Transaction
from schemas.operations.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.schemas import OperationUnion


AuthorityAction = Literal["add-account", "add-key", "remove-account", "remove-key", "modify-account", "modify-key"]


class ProcessCommandBase(ABC):
    def __init__(self, world: World) -> None:
        super().__init__()
        self.world = world
        self._sign_with: str | None = None
        self._save_file: str | Path | None = None
        self._broadcast: bool = False
        self._autosign: bool | None = None

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """Get the operation to be processed."""

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return await self._create_operation()

    async def validate(self) -> None:  # noqa: B027
        """Validate the process command configuration. Override in subclasses as needed."""

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
        # Try to get key from alias first
        try:
            aliased_key = self.world.profile.keys.get_from_alias(key_or_alias)
            return PublicKey(value=aliased_key.value)
        except KeyNotFoundError:
            # If not found as alias, treat it as a public key string
            return PublicKey(value=key_or_alias)

    async def finalize(  # noqa: PLR0913
        self,
        sign_with: list[str] | str | None = None,
        save_file: str | Path | None = None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: Literal["legacy", "hf26"] | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> Transaction:
        """Finalize the operation with specified signing and broadcasting options."""
        # Normalize sign_with to list
        if isinstance(sign_with, str):
            sign_keys_or_aliases = [sign_with]
        elif isinstance(sign_with, list):
            sign_keys_or_aliases = sign_with
        else:
            sign_keys_or_aliases = []

        # Convert aliases to keys
        sign_keys = [self._resolve_key_or_alias(key_or_alias) for key_or_alias in sign_keys_or_aliases]

        # Set instance variables so they're available in _get_transaction_content()
        self._sign_with = sign_keys_or_aliases[0] if sign_keys_or_aliases else None
        self._save_file = save_file
        self._broadcast = broadcast
        self._autosign = autosign
        await self.validate()
        content = await self._get_transaction_content()

        # Handle multiple signatures
        if len(sign_keys) > 1:
            return (
                await self.world.commands.perform_actions_on_transaction(
                    content=content,
                    sign_keys=sign_keys,
                    save_file_path=Path(save_file) if save_file else None,
                    force_save_format=file_format,
                    serialization_mode=serialization_mode,
                    broadcast=broadcast,
                )
            ).result_or_raise

        # Single signature or no signature
        return (
            await self.world.commands.perform_actions_on_transaction(
                content=content,
                sign_key=sign_keys[0] if sign_keys else None,
                autosign=bool(autosign),
                save_file_path=Path(save_file) if save_file else None,
                force_save_format=file_format,
                serialization_mode=serialization_mode,
                broadcast=broadcast,
            )
        ).result_or_raise


class ProcessTransfer(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        from_account: str,
        to: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> None:
        super().__init__(world)
        self.from_account = from_account
        self.to = to
        self.amount = amount
        self.memo = memo

    def _normalize_amount(self) -> Asset.LiquidT:
        """Convert amount to proper Asset.LiquidT type."""
        amount = Asset.from_legacy(self.amount) if isinstance(self.amount, str) else self.amount
        if not isinstance(amount, Asset.LiquidT):
            amount = cast("Asset.LiquidT", amount)
        return amount

    async def _create_operation(self) -> TransferOperation:
        return TransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=self._normalize_amount(),
            memo=self.memo,
        )


class ProcessTransaction(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        already_signed_mode: AlreadySignedMode,
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

    async def _get_transaction_content(self) -> Transaction:
        """Get transaction content from file for ProcessTransaction."""
        cli_transaction = CLIProcessTransaction(
            from_file=self.from_file if self.from_file is not None else None,
            loaded_transaction=self.from_object if self.from_object is not None else None,
            force_unsign=self.force_unsign,
            already_signed_mode=self.already_signed_mode,
            sign_with=self._sign_with,
            broadcast=self._broadcast,
            save_file=str(self._save_file) if self._save_file else None,
            force=self.force,
            autosign=bool(self._autosign) if self._autosign is not None else False,
        )
        await cli_transaction.validate()
        return await cli_transaction.get_transaction()

    async def finalize(  # noqa: PLR0913
        self,
        sign_with: list[str] | str | None = None,
        save_file: str | Path | None = None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: Literal["legacy", "hf26"] | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> Transaction:
        """Finalize the operation with specified signing and broadcasting options."""
        # Normalize sign_with to list
        if isinstance(sign_with, str):
            sign_keys_or_aliases = [sign_with]
        elif isinstance(sign_with, list):
            sign_keys_or_aliases = sign_with
        else:
            sign_keys_or_aliases = []

        # Convert aliases to keys
        sign_keys = [self._resolve_key_or_alias(key_or_alias) for key_or_alias in sign_keys_or_aliases]

        await self.validate()
        content = await self._get_transaction_content()

        # Handle multiple signatures
        if len(sign_keys) > 1:
            return (
                await self.world.commands.perform_actions_on_transaction(
                    content=content,
                    sign_keys=sign_keys,
                    save_file_path=Path(save_file) if save_file else None,
                    force_save_format=file_format,
                    serialization_mode=serialization_mode,
                    broadcast=broadcast,
                    force_unsign=self.force_unsign,
                    already_signed_mode=self.already_signed_mode,
                )
            ).result_or_raise

        # Single signature or no signature
        return (
            await self.world.commands.perform_actions_on_transaction(
                content=content,
                sign_key=sign_keys[0] if sign_keys else None,
                autosign=bool(autosign),
                save_file_path=Path(save_file) if save_file else None,
                force_save_format=file_format,
                serialization_mode=serialization_mode,
                broadcast=broadcast,
                force_unsign=self.force_unsign,
                already_signed_mode=self.already_signed_mode,
            )
        ).result_or_raise

    async def _create_operation(self) -> OperationUnion:
        """ProcessTransaction uses _get_transaction_content() instead."""
        raise NotImplementedError("ProcessTransaction uses _get_transaction_content() instead of _create_operation")


class ProcessAuthority(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int,
    ) -> None:
        super().__init__(world)
        self.authority_type = authority_type
        self.account_name = account_name
        self.threshold = threshold
        self.process_account_update = ProcessAccountUpdate(account_name=account_name)
        self._set_threshold()

    def _set_threshold(self) -> None:
        set_threshold_function = partial(set_threshold, threshold=self.threshold)
        update_function = partial(update_authority, attribute=self.authority_type, callback=set_threshold_function)
        self.process_account_update.add_callback(update_function)

    def _add_authority_callback(self, callback_function: Callable[..., Any]) -> None:
        """Helper method to add callback for authority updates."""
        update_function = partial(update_authority, attribute=self.authority_type, callback=callback_function)
        self.process_account_update.add_callback(update_function)

    def add_key(
        self,
        *,
        key: str,
        weight: int,
    ) -> Self:
        add_key_function = partial(add_key, key=key, weight=weight)
        self._add_authority_callback(add_key_function)
        return self

    def add_account(
        self,
        *,
        account_name: str,
        weight: int,
    ) -> Self:
        add_account_function = partial(add_account, account=account_name, weight=weight)
        self._add_authority_callback(add_account_function)
        return self

    def remove_key(
        self,
        *,
        key: str,
    ) -> Self:
        remove_key_function = partial(remove_key, key=key)
        self._add_authority_callback(remove_key_function)
        return self

    def remove_account(
        self,
        *,
        account: str,
    ) -> Self:
        remove_account_function = partial(remove_account, account=account)
        self._add_authority_callback(remove_account_function)
        return self

    def modify_key(
        self,
        *,
        key: str,
        weight: int,
    ) -> Self:
        modify_key_function = partial(modify_key, key=key, weight=weight)
        self._add_authority_callback(modify_key_function)
        return self

    def modify_account(
        self,
        *,
        account: str,
        weight: int,
    ) -> Self:
        modify_account_function = partial(modify_account, account=account, weight=weight)
        self._add_authority_callback(modify_account_function)
        return self

    async def finalize(  # noqa: PLR0913
        self,
        sign_with: list[str] | str | None = None,
        save_file: str | Path | None = None,
        file_format: Literal["json", "bin"] | None = None,
        serialization_mode: Literal["legacy", "hf26"] | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> Transaction:
        """Finalize the operation with specified signing and broadcasting options."""
        # Normalize sign_with to single string (account update only supports single signature)
        single_sign_with = (sign_with[0] if sign_with else None) if isinstance(sign_with, list) else sign_with

        # Set instance variables first
        self._sign_with = single_sign_with
        self._save_file = save_file
        self._broadcast = broadcast
        self._autosign = autosign
        self.process_account_update.modify_common_options(
            sign_with=single_sign_with,
            broadcast=broadcast,
            save_file=str(save_file) if save_file else None,
            autosign=autosign,
            force_save_format=file_format,
            serialization_mode=serialization_mode,
        )

        await self.validate()
        await self.process_account_update.run()
        return await self.process_account_update.get_transaction()

    async def _get_transaction_content(self) -> Transaction:
        """Get transaction content from ProcessAccountUpdate."""
        # Set the options based on current finalize parameters
        # When called from ProcessMultipleOperations, we need to ensure proper settings
        self.process_account_update.modify_common_options(
            sign_with=self._sign_with,
            broadcast=self._broadcast,
            save_file=str(self._save_file) if self._save_file else None,
            autosign=self._autosign if self._autosign is not None else False,
        )
        # Run the account update to generate the transaction
        await self.process_account_update.run()
        return await self.process_account_update.get_transaction()

    async def _create_operation(self) -> OperationUnion:
        """ProcessAuthority uses ProcessAccountUpdate, so this method is not used directly."""
        raise NotImplementedError("ProcessAuthority uses ProcessAccountUpdate mechanism instead of _create_operation")


class ProcessPowerDownStart(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> None:
        super().__init__(world)
        self.account_name = account_name
        self.amount = amount

    async def _create_operation(self) -> OperationUnion:
        """To be implemented when power down operations are added."""
        raise NotImplementedError("PowerDownStart operation not yet implemented")


class ProcessPowerDownRestart(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> None:
        super().__init__(world)
        self.account_name = account_name
        self.amount = amount

    async def _create_operation(self) -> OperationUnion:
        """To be implemented when power down operations are added."""
        raise NotImplementedError("PowerDownRestart operation not yet implemented")


class ProcessPowerDownCancel(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        account_name: str,
    ) -> None:
        super().__init__(world)
        self.account_name = account_name

    async def _create_operation(self) -> OperationUnion:
        """To be implemented when power down operations are added."""
        raise NotImplementedError("PowerDownCancel operation not yet implemented")


class ProcessPowerUp(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        *,
        force: bool,
    ) -> None:
        super().__init__(world)
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.force = force

    async def _create_operation(self) -> OperationUnion:
        """To be implemented when power up operations are added."""
        raise NotImplementedError("PowerUp operation not yet implemented")


class ProcessCustomJson(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None,
        authorize_by_active: str | list[str] | None,
    ) -> None:
        super().__init__(world)
        self.id_ = id_
        self.json = json
        self.authorize = authorize
        self.authorize_by_active = authorize_by_active

    async def _create_operation(self) -> OperationUnion:
        """To be implemented when custom JSON operations are added."""
        raise NotImplementedError("CustomJson operation not yet implemented")


class ProcessMultipleOperations(ProcessCommandBase):
    """Processor for handling multiple operations in a single transaction."""

    def __init__(
        self,
        world: World,
        operation_builders: list[ProcessCommandBase],
    ) -> None:
        super().__init__(world)
        self.operation_builders = operation_builders
        self._base_transaction: Transaction | None = None

    async def _create_operation(self) -> OperationUnion:
        """Not used for multiple operations - we override _get_transaction_content instead."""
        raise NotImplementedError("ProcessMultipleOperations uses _get_transaction_content() instead")

    async def validate(self) -> None:
        """Validate that signed transactions cannot have operations added to them."""
        from clive.__private.si.exceptions import CannotAddOperationToSignedTransactionError  # noqa: PLC0415

        # Check if any of the operation builders is a ProcessTransaction with a signed transaction
        for builder in self.operation_builders:
            if isinstance(builder, ProcessTransaction):
                # Get the transaction from ProcessTransaction
                transaction_content = await builder._get_transaction_content()
                if transaction_content.is_signed and not builder.force_unsign:
                    raise CannotAddOperationToSignedTransactionError

        await super().validate()

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        """Get all operations from all operation builders and preserve transaction metadata."""
        operations: list[OperationUnion] = []
        base_transaction: Transaction | None = None

        for builder in self.operation_builders:
            # Get content from each operation builder
            content = await builder._get_transaction_content()
            # If content is already a Transaction (e.g., from ProcessTransaction), extract operations and metadata
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
                operation = cast("OperationUnion", content)
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
