from __future__ import annotations

from textual.binding import Binding

from clive.ui.dashboard.dashboard_base import DashboardBase


class DashboardActive(DashboardBase):
    BINDINGS = [
        Binding("f1", "log_out", "Log out"),
        Binding("f2", "transfer", "Transfer"),
    ]

    def action_log_out(self) -> None:
        self.app.deactivate()
        self.app.switch_screen("dashboard_inactive")

    def action_transfer(self) -> None:
        self.log("Transfer action not implemented yet.")
