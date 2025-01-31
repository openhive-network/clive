from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from beekeepy import AsyncWallet

    from clive.__private.core.app_state import AppState, LockSource


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    wallet: AsyncWallet
    app_state: AppState
    source: LockSource = "unknown"

    async def _execute(self) -> None:
        await self.__sync_state()

    async def __sync_state(self) -> None:
        is_unlocked = (await self.wallet.unlocked) is not None
        await self.app_state.unlock() if is_unlocked else self.app_state.lock(self.source)
