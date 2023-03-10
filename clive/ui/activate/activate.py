from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, Input, Static, Switch

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Activate(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Cancel"),
        Binding("f1", "activate", "Activate"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__password_input = Input(placeholder="Password", password=True)

    def on_mount(self) -> None:
        self.__password_input.focus()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Profile name", classes="label")
            yield Input(self.app.profile_data.name, disabled=True)
            yield Static("Password", classes="label", id="password-label")
            yield self.__password_input
            with Static():
                yield Switch(False)
            yield Static("Permanent active mode", classes="label", id="active-mode-label")
            yield Static()
            yield Button("Activate", variant="primary", id="activate-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "activate-button":
            self.action_activate()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_activate(self) -> None:
        self.app.activate()
        self.app.pop_screen()
        self.app.switch_screen("dashboard_active")
