from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Placeholder

from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class DashboardActive(BaseScreen):
    BINDINGS = [
        Binding("f1", "logout", "Logout"),
        Binding("f2", "transfer", "Transfer"),
    ]

    def create_main_panel(self) -> ComposeResult:
        yield Placeholder("DashboardActive content goes here")

    def action_logout(self) -> None:
        self.app.switch_screen("dashboard_inactive")

    def action_transfer(self) -> None:
        self.log("Transfer action not implemented yet.")
