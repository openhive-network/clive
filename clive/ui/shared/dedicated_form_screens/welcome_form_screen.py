from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Button, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.form_screen import FirstFormScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WelcomeFormScreen(BaseScreen, FirstFormScreen):
    def __init__(self, title: str, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        self.__title = title
        super().__init__(name, id, classes)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield BigTitle("welcome")
            yield Static(self.__title)
            yield Button("Start! 🐝", id="welcome_button_start")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "welcome_button_start":
            self.action_next_screen()
