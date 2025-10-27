"""
Chaining interface implementation for Clive SI.

This module implements a fluent API with method chaining for blockchain operations.
The interface is organized into 4 groups of commands that must be called in sequence:

1. Main commands (e.g., transfer, transaction, update_authority)
2. Sub-commands (optional, command-specific, e.g., add_key for update_authority)
3. Signing commands (no_sign, autosign, sign_with)
4. Finalizing commands (broadcast, save_file, get_transaction)

Key constraints:
- Groups must be called in order (group 2 can be skipped)
- Each group can be called only once, except group 2 which can be called multiple times
- Sub-commands (group 2) are specific to each main command and cannot be used with others
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self

from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.si.core.process import (
    ProcessAuthority,
    ProcessCustomJson,
    ProcessPowerDownCancel,
    ProcessPowerDownRestart,
    ProcessPowerDownStart,
    ProcessPowerUp,
    ProcessTransaction,
    ProcessTransfer,
)

if TYPE_CHECKING:
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.asset import Asset
    from clive.__private.models.transaction import Transaction


class ChainError(Exception):
    """Base exception for chaining interface errors."""


class ChainSequenceError(ChainError):
    """Raised when chaining sequence is violated."""


class ChainDuplicateCallError(ChainError):
    """Raised when a group is called more than once (except sub-commands)."""


class ChainInvalidSubcommandError(ChainError):
    """Raised when a sub-command is used with incompatible main command."""


class ChainStage:
    """Tracks the current stage and state of the chaining interface."""
    
    MAIN = 1
    SUB = 2
    SIGNING = 3
    FINALIZING = 4
    
    def __init__(self) -> None:
        self.current_stage = self.MAIN
        self.groups_called: set[int] = set()
        self.main_command_type: str | None = None
    
    def advance_to(self, stage: int, allow_skip_sub: bool = True) -> None:
        """Advance to a new stage, enforcing sequence rules."""
        if stage < self.current_stage:
            raise ChainSequenceError(f"Cannot go back to stage {stage} from {self.current_stage}")
        
        # Allow skipping sub-commands stage
        if stage > self.current_stage + 1 and not (self.current_stage == self.MAIN and stage == self.SIGNING and allow_skip_sub):
            if not (self.current_stage == self.SUB and stage == self.FINALIZING):
                raise ChainSequenceError(f"Cannot skip from stage {self.current_stage} to {stage}")
        
        # Check if group was already called (except sub-commands)
        if stage in self.groups_called and stage != self.SUB:
            raise ChainDuplicateCallError(f"Stage {stage} can only be called once")
        
        self.current_stage = stage
        self.groups_called.add(stage)


class BaseChain(ABC):
    """Base class for all chaining interfaces."""
    
    def __init__(self, world: World) -> None:
        self.world = world
        self._stage = ChainStage()
        self._processor: Any = None
    
    @abstractmethod
    def _create_processor(self) -> Any:
        """Create the appropriate processor for this chain."""


class SigningMixin:
    """Mixin providing signing commands (group 3)."""
    
    def no_sign(self) -> FinalizingChain:
        """Configure transaction to not be signed."""
        self._stage.advance_to(ChainStage.SIGNING)
        return FinalizingChain(self.world, self._processor, sign_method="no_sign")
    
    def autosign(self) -> FinalizingChain:
        """Configure transaction to be auto-signed."""
        self._stage.advance_to(ChainStage.SIGNING)
        return FinalizingChain(self.world, self._processor, sign_method="autosign")
    
    def sign_with(self, key: str) -> FinalizingChain:
        """Configure transaction to be signed with specific key."""
        self._stage.advance_to(ChainStage.SIGNING)
        return FinalizingChain(self.world, self._processor, sign_method="sign_with", sign_key=key)


class FinalizingChain:
    """Handles finalizing commands (group 4)."""
    
    def __init__(
        self,
        world: World,
        processor: Any,
        sign_method: str,
        sign_key: str | None = None,
    ) -> None:
        self.world = world
        self._processor = processor
        self._sign_method = sign_method
        self._sign_key = sign_key
    
    async def broadcast(self) -> Transaction:
        """Broadcast the transaction to the blockchain."""
        return await self._finalize(broadcast=True)
    
    async def save_file(
        self,
        path: str | Path,
        *,
        force_save_format: Literal["json", "bin"] | None = None,
    ) -> Transaction:
        """Save the transaction to a file."""
        return await self._finalize(
            save_file=path,
            force_save_format=force_save_format,
            broadcast=False,
        )
    
    async def get_transaction(self) -> Transaction:
        """Get the transaction without broadcasting or saving."""
        return await self._finalize(broadcast=False)
    
    async def _finalize(
        self,
        *,
        broadcast: bool = False,
        save_file: str | Path | None = None,
        force_save_format: Literal["json", "bin"] | None = None,
    ) -> Transaction:
        """Internal method to finalize the transaction."""
        sign_with = self._sign_key if self._sign_method == "sign_with" else None
        autosign = self._sign_method == "autosign"
        
        return await self._processor.finalize(
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
            force_save_format=force_save_format,
        )


class TransferChain(BaseChain, SigningMixin):
    """Chain interface for transfer operations."""
    
    def __init__(
        self,
        world: World,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "transfer"
        self._from_account = from_account
        self._to_account = to_account
        self._amount = amount
        self._memo = memo
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessTransfer:
        """Create ProcessTransfer instance."""
        return ProcessTransfer(
            world=self.world,
            from_account=self._from_account,
            to=self._to_account,
            amount=self._amount,
            memo=self._memo,
        )


class TransactionChain(BaseChain, SigningMixin):
    """Chain interface for transaction operations."""
    
    def __init__(
        self,
        world: World,
        from_file: str | Path,
        *,
        force_unsign: bool | None = None,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        force: bool = False,
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "transaction"
        self._from_file = from_file
        self._force_unsign = force_unsign
        self._already_signed_mode = already_signed_mode
        self._force = force
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessTransaction:
        """Create ProcessTransaction instance."""
        return ProcessTransaction(
            world=self.world,
            from_file=self._from_file,
            force_unsign=self._force_unsign,
            already_signed_mode=self._already_signed_mode,
            force=self._force,
        )


class AuthorityChain(BaseChain, SigningMixin):
    """Chain interface for authority update operations."""
    
    def __init__(
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int,
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "authority"
        self._authority_type = authority_type
        self._account_name = account_name
        self._threshold = threshold
        self._processor = self._create_processor()
    
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
        self._stage.advance_to(ChainStage.SUB)
        self._processor.add_key(key=key, weight=weight)
        return self
    
    def add_account(self, *, account_name: str, weight: int) -> Self:
        """Add an account to the authority (sub-command)."""
        self._validate_sub_command()
        self._stage.advance_to(ChainStage.SUB)
        self._processor.add_account(account_name=account_name, weight=weight)
        return self
    
    def remove_key(self, *, key: str) -> Self:
        """Remove a key from the authority (sub-command)."""
        self._validate_sub_command()
        self._stage.advance_to(ChainStage.SUB)
        self._processor.remove_key(key=key)
        return self
    
    def remove_account(self, *, account: str) -> Self:
        """Remove an account from the authority (sub-command)."""
        self._validate_sub_command()
        self._stage.advance_to(ChainStage.SUB)
        self._processor.remove_account(account=account)
        return self
    
    def modify_key(self, *, key: str, weight: int) -> Self:
        """Modify a key in the authority (sub-command)."""
        self._validate_sub_command()
        self._stage.advance_to(ChainStage.SUB)
        self._processor.modify_key(key=key, weight=weight)
        return self
    
    def modify_account(self, *, account: str, weight: int) -> Self:
        """Modify an account in the authority (sub-command)."""
        self._validate_sub_command()
        self._stage.advance_to(ChainStage.SUB)
        self._processor.modify_account(account=account, weight=weight)
        return self
    
    def _validate_sub_command(self) -> None:
        """Validate that sub-commands can be called."""
        if self._stage.main_command_type != "authority":
            raise ChainInvalidSubcommandError("Authority sub-commands can only be used with authority operations")


class PowerDownStartChain(BaseChain, SigningMixin):
    """Chain interface for power down start operations."""
    
    def __init__(
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "power_down_start"
        self._account_name = account_name
        self._amount = amount
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessPowerDownStart:
        """Create ProcessPowerDownStart instance."""
        return ProcessPowerDownStart(
            world=self.world,
            account_name=self._account_name,
            amount=self._amount,
        )


class PowerDownRestartChain(BaseChain, SigningMixin):
    """Chain interface for power down restart operations."""
    
    def __init__(
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "power_down_restart"
        self._account_name = account_name
        self._amount = amount
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessPowerDownRestart:
        """Create ProcessPowerDownRestart instance."""
        return ProcessPowerDownRestart(
            world=self.world,
            account_name=self._account_name,
            amount=self._amount,
        )


class PowerDownCancelChain(BaseChain, SigningMixin):
    """Chain interface for power down cancel operations."""
    
    def __init__(
        self,
        world: World,
        account_name: str,
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "power_down_cancel"
        self._account_name = account_name
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessPowerDownCancel:
        """Create ProcessPowerDownCancel instance."""
        return ProcessPowerDownCancel(
            world=self.world,
            account_name=self._account_name,
        )


class PowerUpChain(BaseChain, SigningMixin):
    """Chain interface for power up operations."""
    
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
        self._stage.main_command_type = "power_up"
        self._from_account = from_account
        self._to_account = to_account
        self._amount = amount
        self._force = force
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessPowerUp:
        """Create ProcessPowerUp instance."""
        return ProcessPowerUp(
            world=self.world,
            from_account=self._from_account,
            to_account=self._to_account,
            amount=self._amount,
            force=self._force,
        )


class CustomJsonChain(BaseChain, SigningMixin):
    """Chain interface for custom JSON operations."""
    
    def __init__(
        self,
        world: World,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None = None,
        authorize_by_active: str | list[str] | None = None,
    ) -> None:
        super().__init__(world)
        self._stage.main_command_type = "custom_json"
        self._id = id_
        self._json = json
        self._authorize = authorize
        self._authorize_by_active = authorize_by_active
        self._processor = self._create_processor()
    
    def _create_processor(self) -> ProcessCustomJson:
        """Create ProcessCustomJson instance."""
        return ProcessCustomJson(
            world=self.world,
            id_=self._id,
            json=self._json,
            authorize=self._authorize,
            authorize_by_active=self._authorize_by_active,
        )