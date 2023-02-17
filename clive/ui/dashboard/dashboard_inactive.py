from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Placeholder

from clive.ui.login.login import Login
from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class DashboardInactive(BaseScreen):
    BINDINGS = [Binding("f1", "login", "Login")]

    def create_main_panel(self) -> ComposeResult:
        yield Placeholder("DashboardInactive content goes here")

    def action_login(self) -> None:
        self.app.push_screen(Login())
