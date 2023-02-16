from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Placeholder

from clive.enums import AppMode
from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Login(BaseScreen):
    BINDINGS = [Binding("escape", "dashboard", "Dashboard"), Binding("f1", "login", "Log in")]

    def create_main_panel(self) -> ComposeResult:
        yield Placeholder("Login content goes here")

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_login(self) -> None:
        self.app.app_status.mode = AppMode.ACTIVE
        self.app.pop_screen()


class DashboardInactive(BaseScreen):
    BINDINGS = [
        Binding("f1", "login", "Login"),
    ]

    def create_main_panel(self) -> ComposeResult:
        yield Placeholder("Dashboard content goes here")

    def action_login(self) -> None:
        self.app.push_screen(Login())
