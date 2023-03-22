from __future__ import annotations

from textual.binding import Binding

from clive.ui.config.config_active import ConfigActive
from clive.ui.dashboard.dashboard_base import DashboardBase
from clive.ui.operations.operations import Operations


class DashboardActive(DashboardBase):
    BINDINGS = [
        Binding("f2", "operations", "Operations"),
        Binding("f4", "deactivate", "Deactivate"),
        Binding("f9", "config", "Config"),
    ]

    def action_deactivate(self) -> None:
        self.app.deactivate()

    def action_operations(self) -> None:
        self.app.push_screen(Operations())

    def action_config(self) -> None:
        self.app.push_screen(ConfigActive())
