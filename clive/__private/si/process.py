from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.si.core.process.chaining import (
    AuthorityUpdateChain,
    ChainableOperationBuilder,
)
from clive.__private.si.core.process.process import (
    OperationBuilder,
    TransactionBuilder,
    TransferBuilder,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.asset import Asset
    from clive.__private.models.transaction import Transaction
    from clive.__private.si.base import UnlockedCliveSi
    from clive.__private.si.core.process.process import OperationBuilder


class OperationsBuilderInterface:
    """
    Base interface for building blockchain operations.

    This class provides common methods for creating operations (transfers, authority updates)
    and manages the chain of operations being built. It serves as foundation for both:
    - Initial operation building (starting from a profile)
    - Chaining context (continuing with existing operations)

    Each operation method returns a chain object that allows further configuration,
    chaining additional operations, and finalizing (broadcast/save/get transaction).
    """

    def __init__(self, world: World, all_operations: list[OperationBuilder] | None = None) -> None:
        self.world = world
        self._all_operations: list[OperationBuilder] = all_operations or []

    def transfer(
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> ChainableOperationBuilder:
        """Transfer funds between accounts."""
        chain = ChainableOperationBuilder(world=self.world, previous_operations=self._all_operations)
        chain._current_operation = TransferBuilder(
            world=self.world,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            memo=memo,
        )
        return chain

    def update_owner_authority(
        self,
        account_name: str,
        *,
        threshold: int | None = None,
    ) -> AuthorityUpdateChain:
        """Update owner authority for an account."""
        return self._update_authority("owner", account_name, threshold)

    def update_active_authority(
        self,
        account_name: str,
        *,
        threshold: int | None = None,
    ) -> AuthorityUpdateChain:
        """Update active authority for an account."""
        return self._update_authority("active", account_name, threshold)

    def update_posting_authority(
        self,
        account_name: str,
        *,
        threshold: int | None = None,
    ) -> AuthorityUpdateChain:
        """Update posting authority for an account."""
        return self._update_authority("posting", account_name, threshold)

    def _update_authority(
        self,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int | None,
    ) -> AuthorityUpdateChain:
        """Common method for updating authority."""
        return AuthorityUpdateChain(
            world=self.world,
            authority_type=authority_type,
            account_name=account_name,
            threshold=threshold,
            previous_operations=self._all_operations,
        )


class ProfileOperationsInterface(OperationsBuilderInterface):
    """
    Interface for processing blockchain operations from a profile context.

    This is the main entry point for building operations when working with a profile.
    Provides methods for:
    - Transfers (transfer)
    - Authority updates (update_owner_authority, update_active_authority, update_posting_authority)
    - Transaction loading (transaction, transaction_from_object)

    All operations return chainable builders that can be configured, combined with
    other operations (.process), and finalized (broadcast/save/as_transaction_object).
    """

    def __init__(self, clive_instance: UnlockedCliveSi) -> None:
        super().__init__(world=clive_instance._world, all_operations=None)
        self.clive = clive_instance

    def transaction(
        self,
        from_file: str | Path,
        *,
        force_unsign: bool = False,
        already_signed_mode: AlreadySignedMode | None = None,
        force: bool = False,
    ) -> ChainableOperationBuilder:
        """Process a transaction from a file. Can only be used at the start of a chain."""
        chain = ChainableOperationBuilder(world=self.world, previous_operations=self._all_operations)
        chain._current_operation = TransactionBuilder(
            world=self.world,
            from_file=from_file,
            force_unsign=force_unsign,
            already_signed_mode=already_signed_mode,
            force=force,
        )
        return chain

    def transaction_from_object(
        self,
        from_object: Transaction | None,
        *,
        force_unsign: bool = False,
        already_signed_mode: AlreadySignedMode | None = None,
        force: bool = False,
    ) -> ChainableOperationBuilder:
        """Process a transaction from an object. Can only be used at the start of a chain."""
        chain = ChainableOperationBuilder(world=self.world, previous_operations=self._all_operations)
        chain._current_operation = TransactionBuilder(
            world=self.world,
            from_file=None,
            from_object=from_object,
            force_unsign=force_unsign,
            already_signed_mode=already_signed_mode,
            force=force,
        )
        return chain


class ChainingOperationsInterface(OperationsBuilderInterface):
    """
    Interface for processing blockchain operations in a chaining context.

    This interface is returned by the .process property of chain objects,
    allowing you to add more operations to an existing chain. It maintains
    the list of previously built operations and provides the same operation
    methods as ProfileOperationsInterface.
    """

    def __init__(self, world: World, all_operations: list[OperationBuilder]) -> None:
        super().__init__(world=world, all_operations=all_operations)
