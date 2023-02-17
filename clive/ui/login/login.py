from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Input, Static, Switch

from clive.ui.registration.registration import Registration
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.focusable_link import FocusableLink

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Login(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "login", "Login"),
        Binding("f2", "register", "Register"),
    ]

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def create_main_panel(self) -> ComposeResult:
        yield Container(
            Static("Username", classes="label"),
            Input(placeholder="Username"),
            Static("Password", classes="label"),
            Input(placeholder="Password", password=True),
            Switch(False),
            Static("Permanent active mode", classes="label", id="active-mode-label"),
            Static(),
            Button("Login", variant="primary", id="login-button"),
            Static(),
            FocusableLink("Don't have an account yet?", self.action_register),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-button":
            self.action_login()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_login(self) -> None:
        self.app.pop_screen()
        self.app.switch_screen("dashboard_active")

    def action_register(self) -> None:
        self.app.push_screen(Registration())
