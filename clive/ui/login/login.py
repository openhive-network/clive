from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, Input, Static, Switch

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Login(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "log_in", "Log in"),
    ]

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def create_main_panel(self) -> ComposeResult:
        yield DialogContainer(
            Static("Password", classes="label"),
            Input(placeholder="Password", password=True),
            Switch(False),
            Static("Permanent active mode", classes="label", id="active-mode-label"),
            Static(),
            Button("Log in", variant="primary", id="log-in-button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "log-in-button":
            self.action_log_in()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_log_in(self) -> None:
        self.app.activate()
        self.app.pop_screen()
        self.app.switch_screen("dashboard_active")
