from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Static

from clive.__private.storage.contextual import ContextT
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.shared.form_screen import LastFormScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class Description(Static):
    """Some description text"""


class ButtonsContainer(Horizontal):
    """Container holding buttons"""


class FinishFormScreen(BaseScreen, LastFormScreen[ContextT]):
    BINDINGS = [Binding("f10", "finish", "Ok")]

    def __init__(self, owner: Form[ContextT], end_note: str) -> None:
        self.__end_note = end_note
        super().__init__(owner)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("done!"):
            yield Description(self.__end_note)
            with ButtonsContainer():
                yield CliveButton("Finish 🎉", id_="finish_return_form_screen")
                yield CliveButton("Forgot something? 🤔", id_="return_finish_form_screen")

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
