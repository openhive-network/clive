from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.core.constants.tui.messages import PRESS_HELP_MESSAGE
from clive.__private.ui.forms.form_screen import FormScreen
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.forms.form import Form


class Description(Static):
    """Description of the welcome screen."""


class CreateProfileWelcomeFormScreen(BaseScreen, FormScreen):
    BINDINGS = [Binding("f1", "help", "Help")]
    CSS_PATH = [get_relative_css_path(__file__)]
    SHOW_RAW_HEADER = True

    def __init__(self, owner: Form) -> None:
        super().__init__(owner)
        self._description = "Let's create profile!\n" + PRESS_HELP_MESSAGE
        self.back_screen_mode = "nothing_to_back"

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome"):
            yield Description(self._description)
            yield CliveButton("Start!", id_="welcome-button-start")

    @on(CliveButton.Pressed, "#welcome-button-start")
    async def begin(self) -> None:
        await self.action_next_screen()

    async def apply(self) -> None:
        """Nothing to apply - user just started the form."""

    async def validate(self) -> None:
        """Nothing to check - the user could not have pressed the button in the wrong way :)."""
