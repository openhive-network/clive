from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.dashboard.dashboard_base import DashboardBase


class DashboardUnlocked(DashboardBase):
    BINDINGS = [
        Binding("f4", "lock", "Lock wallet"),
    ]

    async def action_lock(self) -> None:
        await self.commands.lock()
