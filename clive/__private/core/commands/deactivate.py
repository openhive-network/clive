from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.models.aliased import UnlockedWallet


@dataclass(kw_only=True)
class Deactivate(Command):
    app_state: AppState
    wallet: UnlockedWallet | None

    async def _execute(self) -> None:
        if self.wallet is None:
            return

        await self.wallet.lock()
        self.app_state.deactivate()
