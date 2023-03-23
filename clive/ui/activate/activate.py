from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Input, Static, Switch

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.dialog_container import DialogContainer
from clive.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class Activate(BaseScreen):
    BINDINGS = [
        Binding("escape", "dashboard", "Cancel"),
        Binding("f2", "activate", "Ok"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__password_input = Input(placeholder="Password", password=True)
        self.__permanent_active_mode_switch = Switch(False)
        self.__temporary_active_mode_label = Static("Active mode time (minutes)", classes="label")
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
            with ButtonsContainer():
                yield Button("Ok", variant="primary", id="activate-button")
                yield Button("Cancel", variant="error", id="cancel-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "activate-button":
            self.action_activate()
        elif event.button.id == "cancel-button":
            self.action_dashboard()

    def on_switch_changed(self) -> None:
        self.__temporary_active_mode_label.toggle_class("-hidden")
        self.__temporary_active_mode_input.toggle_class("-hidden")

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_activate(self) -> None:
        permanent_active = self.__permanent_active_mode_switch.value
        active_mode_time: timedelta | None = None

        if not permanent_active:
            raw_active_mode_time = self.__get_active_mode_time()
            if raw_active_mode_time is None:
                Notification("The active mode time must be a number and >= 1", category="error").show()
                return

            active_mode_time = timedelta(minutes=raw_active_mode_time)

        self.app.pop_screen()
        self.app.activate(permanent_active, active_mode_time)

    def __get_active_mode_time(self) -> int | None:
        try:
            value = int(self.__temporary_active_mode_input.value)
            return value if value >= 1 else None
        except ValueError:
            return None
