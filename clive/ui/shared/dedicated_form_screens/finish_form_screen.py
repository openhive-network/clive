from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Button, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.ui.shared.form_screen import LastFormScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class FinishFormScreen(BaseScreen, LastFormScreen):
    BINDINGS = [Binding("f10", "finish", "Save")]

    def __init__(
        self, end_note: str, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        self.__end_note = end_note
        super().__init__(name, id, classes)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield BigTitle("done!")
            yield Static(self.__end_note)
            with Container():
                yield Button("Finish 🎉", id="finish_return_form_screen")
                yield Button("Forgot something? 🤔", id="return_finish_form_screen")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "return_finish_form_screen":
            self.action_previous_screen()
        elif event.button.id == "finish_return_form_screen":
            self.action_finish()

    def action_finish(self) -> None:
        while not isinstance(self.app.pop_screen(), WelcomeFormScreen):
            self.log.debug("popping screens in form!")
        self.app.pop_screen()  # and finally pop WelcomeFormScreen
        self.app.switch_screen("dashboard_inactive")
