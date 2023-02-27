from __future__ import annotations

from typing import TYPE_CHECKING

from textual._compose import compose
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Input, Placeholder, Static, Switch

from clive.ui.registration.registration import Registration
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.focusable_link import FocusableLink

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Login(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "log_in", "Log in"),
        Binding("f2", "registration", "Registration"),
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
            Button("Log in", variant="primary", id="log-in-button"),
            Static(),
            FocusableLink("Don't have an account yet?", self.action_registration),
            id="dialog",
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

    def action_registration(self) -> None:
        self.app.push_screen(Registration())

    def as_form(self):
        container: Container = next(self.create_main_panel())
        for widget in container.children:
            if isinstance(widget, FocusableLink):
                continue
            yield widget
