from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Button, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.form_screen import FirstFormScreen
from clive.ui.widgets.clive_button import CliveButton
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WelcomeFormScreen(BaseScreen, FirstFormScreen):
    def __init__(self, title: str) -> None:
        self.__title = title
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome"):
            yield Static(self.__title)
            yield CliveButton("Start! 🐝", id_="welcome_button_start")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "welcome_button_start":
            self.action_next_screen()
