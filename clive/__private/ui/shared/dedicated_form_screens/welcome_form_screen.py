from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.storage.contextual import ContextT
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FirstFormScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class WelcomeFormScreen(BaseScreen, FirstFormScreen[ContextT]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, owner: Form[ContextT], title: str) -> None:
        self.__title = title
        super().__init__(owner)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome"):
            yield Static(self.__title, id="title")
            yield CliveButton("Start!", id_="welcome_button_start")

    @on(CliveButton.Pressed, "#welcome_button_start")
    def begin(self) -> None:
        self.action_next_screen()

    def action_cancel(self) -> None:
        self._cancel()

    def _cancel(self) -> None:
        self.app.pop_screen()
