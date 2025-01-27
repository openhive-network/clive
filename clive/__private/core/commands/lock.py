from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy import AsyncUnlockedWallet

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from beekeepy import AsyncWallet

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Lock(Command):
    app_state: AppState
    wallet: AsyncUnlockedWallet | AsyncWallet

    async def _execute(self) -> None:
        if isinstance(self.wallet, AsyncUnlockedWallet):
            await self.wallet.lock()
        self.app_state.lock()
