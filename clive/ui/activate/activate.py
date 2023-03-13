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
        self.__permanent_active_mode_switch = Switch(False)
        self.__temporary_active_mode_label = Static("Active mode time", classes="label")
        self.__temporary_active_mode_input = Input("60", placeholder="Time in minutes", id="active-mode-input")

    def on_mount(self) -> None:
        self.__password_input.focus()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Profile name", classes="label")
            yield Input(self.app.profile_data.name, disabled=True)
            yield Static("Password", classes="label", id="password-label")
            yield self.__password_input
            with Static():
                yield self.__permanent_active_mode_switch
            yield Static("Permanent active mode", classes="label", id="active-mode-label")
            yield self.__temporary_active_mode_label
            yield self.__temporary_active_mode_input
            yield Static()
            yield Button("Activate", variant="primary", id="activate-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "activate-button":
            self.action_activate()

    def on_switch_changed(self) -> None:
        self.__temporary_active_mode_label.toggle_class("-hidden")
        self.__temporary_active_mode_input.toggle_class("-hidden")

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_activate(self) -> None:
        permanent_active = self.__permanent_active_mode_switch.value

        self.app.activate(permanent_active)
        self.app.pop_screen()
        self.app.switch_screen("dashboard_active")
