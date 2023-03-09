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
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "activate", "Activate"),
    ]

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def create_main_panel(self) -> ComposeResult:
        yield DialogContainer(
            Static("Profile name", classes="label"),
            Input(self.app.profile_data.name, disabled=True),
            Static("Password", classes="label"),
            Input(placeholder="Password", password=True),
            Switch(False),
            Static("Permanent active mode", classes="label", id="active-mode-label"),
            Static(),
            Button("Activate", variant="primary", id="activate-button"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "activate-button":
            self.action_activate()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_activate(self) -> None:
        self.app.activate()
        self.app.pop_screen()
        self.app.switch_screen("dashboard_active")
