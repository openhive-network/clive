from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.config.config_active import ConfigActive
from clive.__private.ui.dashboard.dashboard_base import DashboardBase


class DashboardActive(DashboardBase):
    BINDINGS = [
        Binding("f4", "deactivate", "Deactivate"),
        Binding("f9", "config", "Config"),
    ]

    async def action_deactivate(self) -> None:
        await self.app.world.commands.deactivate()

    def action_config(self) -> None:
        self.app.push_screen(ConfigActive())
