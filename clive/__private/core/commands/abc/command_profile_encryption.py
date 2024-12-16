from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError, CommandRestricted
from clive.__private.core.commands.exceptions import ProfileEncryptionKeyAmountError
from clive.__private.core.commands.is_wallet_unlocked import IsWalletUnlocked

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.models.schemas import PublicKey


class CommandProfileEncryptionError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandProfileEncryption) -> None:
        super().__init__(command, reason="requires unlocked profile encryption wallet")


@dataclass(kw_only=True)
class CommandProfileEncryption(CommandRestricted, ABC):
    """A command that requires profile encryption wallet unlocked."""

    unlocked_profile_encryption_wallet: AsyncUnlockedWallet

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandProfileEncryptionError

    @property
    def encryption_wallet_name(self) -> str:
        return self.unlocked_profile_encryption_wallet.name

    @property
    async def encryption_public_key(self) -> PublicKey:
        keys = await self.unlocked_profile_encryption_wallet.public_keys
        if len(keys) != 1:
            raise ProfileEncryptionKeyAmountError(self, len(keys))
        return keys[0]

    async def _is_execution_possible(self) -> bool:
        return await IsWalletUnlocked(wallet=self.unlocked_profile_encryption_wallet).execute_with_result()
