from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import Button, Input, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.dialog_container import DialogContainer
from clive.ui.widgets.focusable_link import FocusableLink

if TYPE_CHECKING:
    from textual.app import ComposeResult


class RegistrationCommon(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Profile name", classes="label")
            yield Input(self.app.profile_data.name, placeholder="e.x.: Master", id="profile_name_input")
            yield Static("Password", classes="label")
            yield Input(placeholder="Password", password=True, id="password_input")
            yield Static("Repeat password", classes="label")
            yield Input(placeholder="Repeat Password", password=True, id="repeat_password_input")
            yield from self._panel_extras()

    def _panel_extras(self) -> ComposeResult:
        yield Static()

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def save_profile_data(self) -> None:
        minimum_input_length: Final[int] = 3

        profile_name = self.get_widget_by_id("profile_name_input", expect_type=Input).value
        password = self.get_widget_by_id("password_input", expect_type=Input).value
        repeated_password = self.get_widget_by_id("repeat_password_input", expect_type=Input).value

        if all(
            [
                len(profile_name) >= minimum_input_length,
                len(password) >= minimum_input_length,
                (password == repeated_password),
            ]
        ):
            self.app.profile_data.name = profile_name
            self.app.profile_data.password = password
            self.app.update_reactive("profile_data")


class Registration(RegistrationCommon):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "register", "Register"),
        Binding("f2", "login", "Login"),
    ]

    def _panel_extras(self) -> ComposeResult:
        yield Static()
        yield Button("Register", variant="primary", id="register-button")
        yield Static()
        yield FocusableLink("Login instead", self.action_login)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register-button":
            self.action_register()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_register(self) -> None:
        self.save_profile_data()
        self.app.pop_screen()

    def action_login(self) -> None:
        self.app.pop_screen()


class RegistrationForm(RegistrationCommon, FormScreen):
    BINDINGS = [Binding("f10", "save", "Save")]

    def action_save(self) -> None:
        self.save_profile_data()
