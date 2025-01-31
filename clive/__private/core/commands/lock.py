from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Lock(Command):
    app_state: AppState
    unlocked_wallet: AsyncUnlockedWallet

    async def _execute(self) -> None:
        await self.unlocked_wallet.lock()
        self.app_state.lock()
