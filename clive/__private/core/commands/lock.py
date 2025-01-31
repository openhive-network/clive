from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Lock(CommandInUnlocked):
    app_state: AppState

    async def _execute(self) -> None:
        await self.unlocked_wallet.lock()
        self.app_state.lock()
