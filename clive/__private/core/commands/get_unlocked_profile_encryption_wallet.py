from __future__ import annotations

from dataclasses import dataclass

from beekeepy import AsyncSession, AsyncUnlockedWallet

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import (
    MultipleEncryptionWalletsUnlockedError,
    NoEncryptionWalletUnlockedError,
)
from clive.__private.core.encryption import EncryptionService


@dataclass(kw_only=True)
class GetUnlockedProfileEncryptionWallet(CommandWithResult[AsyncUnlockedWallet]):
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
