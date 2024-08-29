from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.screens.dashboard import DashboardBase


class DashboardUnlocked(DashboardBase):
    BINDINGS = [
        Binding("f5", "lock", "Lock wallet"),
    ]

    async def action_lock(self) -> None:
        await self.commands.lock()
