from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from beekeepy import AsyncSession

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class LockAll(Command):
    """Lock all the wallets in the given beekeeper session."""

    app_state: AppState | None = None
    session: AsyncSession

    async def _execute(self) -> None:
        await self.session.lock_all()
        if self.app_state:
            self.app_state.lock()
