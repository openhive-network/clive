from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.activate.activate import Activate
from clive.__private.ui.dashboard.dashboard_base import DashboardBase


class DashboardInactive(DashboardBase):
    BINDINGS = [
        Binding("f4", "activate", "Activate"),
    ]

    def action_activate(self) -> None:
        self.app.push_screen(Activate())
