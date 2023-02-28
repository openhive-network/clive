from __future__ import annotations

from typing import Iterable

from textual.binding import Binding
from textual.widgets import Button

from clive.ui.config.config_base import ConfigBase


class ConfigActive(ConfigBase):
    BINDINGS = [
        Binding("f2", "mock", "Mock"),
    ]

    def additional_buttons(self) -> Iterable[Button]:
        yield Button("Mock", id="mock")

    def action_mock(self) -> None:
        self.app.deactivate()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "mock":
            self.action_mock()
