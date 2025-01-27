from __future__ import annotations

from dataclasses import dataclass

from beekeepy import AsyncSession, AsyncUnlockedWallet

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import MultipleProfilesUnlockedError, NoProfileUnlockedError


@dataclass(kw_only=True)
class GetUnlockedWallet(CommandWithResult[AsyncUnlockedWallet]):
    session: AsyncSession

    async def _execute(self) -> None:
        unlocked = await self.session.wallets_unlocked
        if len(unlocked) > 1:
            raise MultipleProfilesUnlockedError(self)
        if len(unlocked) < 1:
            raise NoProfileUnlockedError(self)
        self._result = unlocked[0]
