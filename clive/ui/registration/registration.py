from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Input, Static

from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.focusable_link import FocusableLink

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Registration(FormScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "register", "Register"),
        Binding("f2", "login", "Login"),
    ]

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def create_main_panel(self) -> ComposeResult:
        yield Container(
            Static("Profile name", classes="label"),
            Input(placeholder="e.x.: Master", id="profile_name_input"),
            Static("Password", classes="label"),
            Input(placeholder="Password", password=True, id="password_input"),
            Static("Repeat password", classes="label"),
            Input(placeholder="Repeat Password", password=True, id="repeat_password_input"),
            Static(),
            Button("Register", variant="primary", id="register-button"),
            Static(),
            FocusableLink("Login instead", self.action_login) if not self.is_form() else Static(),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register-button":
            self.action_register()

    def action_dashboard(self) -> None:
        if not self.is_form():
            self.app.pop_screen()

    def action_register(self) -> None:
        if not self.is_form():
            self.app.pop_screen()

    def action_login(self) -> None:
        if not self.is_form():
            self.app.pop_screen()
