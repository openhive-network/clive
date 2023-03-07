from __future__ import annotations

from typing import Iterable

from textual.binding import Binding
from textual.widgets import Button

from clive.ui.config.config_base import ConfigBase
from clive.ui.manage_authorities import ManageAuthorities


class ConfigActive(ConfigBase):
    BINDINGS = [
        Binding("f2", "manage_authorities", "Manage authorities"),
    ]

    def additional_buttons(self) -> Iterable[Button]:
        yield Button("Manage authorities", id="manage-authorities")

    def action_mock(self) -> None:
        self.app.deactivate()

    def action_manage_authorities(self) -> None:
        self.app.push_screen(ManageAuthorities())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "manage-authorities":
            self.action_manage_authorities()
