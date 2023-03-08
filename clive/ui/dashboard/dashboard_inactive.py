from __future__ import annotations

from textual.binding import Binding

from clive.ui.activate.activate import Activate
from clive.ui.config.config_inactive import ConfigInactive
from clive.ui.dashboard.dashboard_base import DashboardBase


class DashboardInactive(DashboardBase):
    BINDINGS = [
        Binding("c", "config", "Config"),
        Binding("f1", "activate", "Activate"),
    ]

    def action_activate(self) -> None:
        self.app.push_screen(Activate())

    def action_config(self) -> None:
        self.app.push_screen(ConfigInactive())
