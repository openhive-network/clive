from __future__ import annotations

from dataclasses import dataclass

from beekeepy import AsyncSession, AsyncUnlockedWallet

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import MultipleProfilesUnlockedError, NoProfileUnlockedError
from clive.__private.core.encryption import EncryptionService


@dataclass(kw_only=True)
class GetUnlockedUserWallet(CommandWithResult[AsyncUnlockedWallet]):
    """Get the unlocked user wallet - the one containing keys imported by user."""

    session: AsyncSession

    async def _execute(self) -> None:
        unlocked = [
            wallet
            for wallet in await self.session.wallets_unlocked
            if not EncryptionService.is_encryption_wallet_name(wallet.name)
        ]
        if len(unlocked) > 1:
            raise MultipleProfilesUnlockedError(self)
        if len(unlocked) < 1:
            raise NoProfileUnlockedError(self)
        self._result = unlocked[0]
