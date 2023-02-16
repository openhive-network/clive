from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Placeholder

from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Login(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
    ]

    def create_main_panel(self) -> ComposeResult:
        yield Placeholder("Login content goes here")

    def action_dashboard(self) -> None:
        self.app.pop_screen()
