from __future__ import annotations

from typing import Iterable

from textual.widgets import Button

from clive.ui.config.config_base import ConfigBase
from clive.ui.manage_authorities import ManageAuthorities


class ConfigActive(ConfigBase):
    def additional_buttons(self) -> Iterable[Button]:
        yield Button("Manage authorities", id="manage-authorities")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "manage-authorities":
            self.app.push_screen(ManageAuthorities())
