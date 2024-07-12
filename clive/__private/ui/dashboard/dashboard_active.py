from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.dashboard.dashboard_base import DashboardBase


class DashboardActive(DashboardBase):
    BINDINGS = [
        Binding("f4", "deactivate", "Deactivate"),
    ]

    async def action_deactivate(self) -> None:
        await self.commands.deactivate()
