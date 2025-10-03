from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.si.core.process.chaining import (
    AuthorityChain,
    BaseChain,
)
from clive.__private.si.core.process.process import (
    ProcessCommandBase,
    ProcessTransaction,
    ProcessTransfer,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.core.world import World
    from clive.__private.models.asset import Asset
    from clive.__private.models.transaction import Transaction
    from clive.__private.si.base import ProfileBase
    from clive.__private.si.core.process.process import ProcessCommandBase


class ProcessInterfaceBase:
    """Base class for process interfaces with common operation methods."""

    def __init__(self, world: World, operation_builders: list[ProcessCommandBase] | None = None) -> None:
        self.world = world
        self._operation_builders: list[ProcessCommandBase] = operation_builders or []

    def transfer(
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> BaseChain:
        """Transfer funds between accounts."""
        base_chain = BaseChain(world=self.world, operation_builders=self._operation_builders)
        base_chain._operation_builder = ProcessTransfer(
            world=self.world,
            from_account=from_account,
            to=to_account,
            amount=amount,
            memo=memo,
        )
        return base_chain

    def update_owner_authority(
        self,
        account_name: str,
        *,
        threshold: int,
    ) -> AuthorityChain:
        """Update owner authority for an account."""
        return AuthorityChain(
            world=self.world,
            authority_type="owner",
            account_name=account_name,
            threshold=threshold,
            operation_builders=self._operation_builders,
        )

    def update_active_authority(
        self,
        account_name: str,
        *,
        threshold: int,
    ) -> AuthorityChain:
        """Update active authority for an account."""
        return AuthorityChain(
            world=self.world,
            authority_type="active",
            account_name=account_name,
            threshold=threshold,
            operation_builders=self._operation_builders,
        )

    def update_posting_authority(
        self,
        account_name: str,
        *,
        threshold: int,
    ) -> AuthorityChain:
        """Update posting authority for an account."""
        return AuthorityChain(
            world=self.world,
            authority_type="posting",
            account_name=account_name,
            threshold=threshold,
            operation_builders=self._operation_builders,
        )


class ProcessInterface(ProcessInterfaceBase):
    """Interface for processing blockchain operations (transfers, authorities, power, custom JSON)."""

    def __init__(self, clive_instance: ProfileBase) -> None:
        super().__init__(world=clive_instance.world, operation_builders=None)
        self.clive = clive_instance

    def transaction(
        self,
        from_file: str | Path,
        *,
        force_unsign: bool = False,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        force: bool = False,
    ) -> BaseChain:
        """Process a transaction from a file. Can only be used at the start of a chain."""
        base_chain = BaseChain(world=self.world, operation_builders=self._operation_builders)
        base_chain._operation_builder = ProcessTransaction(
            world=self.world,
            from_file=from_file,
            force_unsign=force_unsign,
            already_signed_mode=already_signed_mode,
            force=force,
        )
        return base_chain

    def transaction_from_object(
        self,
        from_object: Transaction | None,
        *,
        force_unsign: bool = False,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        force: bool = False,
    ) -> BaseChain:
        """Process a transaction from an object. Can only be used at the start of a chain."""
        base_chain = BaseChain(world=self.world, operation_builders=self._operation_builders)
        base_chain._operation_builder = ProcessTransaction(
            world=self.world,
            from_file=None,
            from_object=from_object,
            force_unsign=force_unsign,
            already_signed_mode=already_signed_mode,
            force=force,
        )
        return base_chain


class ProcessInterfaceChaining(ProcessInterfaceBase):
    """Interface for processing blockchain operations in a chaining context (with existing operations)."""

    def __init__(self, world: World, operation_builders: list[ProcessCommandBase]) -> None:
        super().__init__(world=world, operation_builders=operation_builders)
