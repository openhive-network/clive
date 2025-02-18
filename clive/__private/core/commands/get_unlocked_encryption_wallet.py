from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from beekeepy import AsyncSession, AsyncUnlockedWallet

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.encryption import EncryptionService


class MultipleEncryptionWalletsUnlockedError(CommandError):
    MESSAGE: Final[str] = "Multiple encryption wallets are unlocked on the beekeeper. There should be only one."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


class NoEncryptionWalletUnlockedError(CommandError):
    MESSAGE: Final[str] = "There is no unlocked encryption wallet on the beekeeper. There should be only one."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


@dataclass(kw_only=True)
class GetUnlockedEncryptionWallet(CommandWithResult[AsyncUnlockedWallet]):
    """Get the unlocked encryption wallet - the one containing encryption key managed by clive."""

    session: AsyncSession

    async def _execute(self) -> None:
        unlocked = [
            wallet
            for wallet in await self.session.wallets_unlocked
            if EncryptionService.is_encryption_wallet_name(wallet.name)
        ]
        if len(unlocked) > 1:
            raise MultipleEncryptionWalletsUnlockedError(self)
        if len(unlocked) < 1:
            raise NoEncryptionWalletUnlockedError(self)
        self._result = unlocked[0]
