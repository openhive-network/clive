from __future__ import annotations

from textual.binding import Binding

from clive.ui.dashboard.dashboard_base import DashboardBase
from clive.ui.login.login import Login


class DashboardInactive(DashboardBase):
    BINDINGS = [Binding("f1", "login", "Login")]

    def action_login(self) -> None:
        self.app.push_screen(Login())
