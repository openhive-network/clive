from __future__ import annotations

from textual.binding import Binding

from clive.ui.activate.activate import Activate
from clive.ui.config.config_inactive import ConfigInactive
from clive.ui.create_profile.create_profile import CreateProfile
from clive.ui.dashboard.dashboard_base import DashboardBase


class DashboardInactive(DashboardBase):
    BINDINGS = [
        Binding("c", "config", "Config"),
        Binding("f1", "activate", "Activate"),
        Binding("f2", "create_profile", "Create profile"),
    ]

    def action_activate(self) -> None:
        if self.app.app_state.permanent_active:
            self.app.activate(True)
        else:
            self.app.push_screen(Activate())

    def action_config(self) -> None:
        self.app.push_screen(ConfigInactive())

    def action_create_profile(self) -> None:
        self.app.push_screen(CreateProfile())
