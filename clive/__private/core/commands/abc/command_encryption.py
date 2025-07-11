from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError
from clive.__private.core.commands.is_wallet_unlocked import IsWalletUnlocked

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.models.schemas import PublicKey


class CommandRequiresUnlockedEncryptionWalletError(CommandExecutionNotPossibleError):
    """
    Error raised when no encryption wallet is available for a command that requires it.

    Since the regular user wallet should always be unlocked when the encryption wallet is unlocked and required,
    this error is raised when either one of both wallets is not unlocked (user wallet or encryption wallet).

    Args:
        command: The command that requires an unlocked encryption wallet.
    """

    def __init__(self, command: CommandEncryption) -> None:
        super().__init__(command, reason="requires both unlocked user wallet and encryption wallet.")


class EncryptionKeyAmountError(CommandError):
    def __init__(self, command: Command, number_of_keys: int) -> None:
        message = (
            f"Error retrieving encryption key. Number of keys: {number_of_keys}. There should be one and only one key."
        )
        super().__init__(command, message)


@dataclass(kw_only=True)
class CommandEncryption(CommandInUnlocked, ABC):
    """
    A command that requires both unlocked user wallet and encryption wallet.

    Attributes:
        unlocked_encryption_wallet: The unlocked encryption wallet to use for the command.
    """

    unlocked_encryption_wallet: AsyncUnlockedWallet

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = (
        CommandRequiresUnlockedEncryptionWalletError
    )

    @property
    def encryption_wallet_name(self) -> str:
        return self.unlocked_encryption_wallet.name

    @property
    async def encryption_public_key(self) -> PublicKey:
        keys = await self.unlocked_encryption_wallet.public_keys
        if len(keys) != 1:
            raise EncryptionKeyAmountError(self, len(keys))
        return keys[0]

    async def _is_execution_possible(self) -> bool:
        return (
            await super()._is_execution_possible()
            and await IsWalletUnlocked(wallet=self.unlocked_encryption_wallet).execute_with_result()
        )
