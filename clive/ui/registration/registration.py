from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Input, Static

from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Registration(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "register", "Register"),
        Binding("f2", "login", "Login"),
    ]

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def create_main_panel(self) -> ComposeResult:
        yield Container(
            Static("Username", classes="label"),
            Input(placeholder="Username"),
            Static("Password", classes="label"),
            Input(placeholder="Password", password=True),
            Static("Repeat password", classes="label"),
            Input(placeholder="Repeat Password", password=True),
            Static(),
            Button("Register", variant="primary", id="register-button"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register-button":
            self.action_register()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_register(self) -> None:
        self.app.pop_screen()

    def action_login(self) -> None:
        self.app.pop_screen()
