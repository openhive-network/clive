from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.core.constants.tui.global_bindings import SHOW_HELP
from clive.__private.core.constants.tui.messages import PRESS_HELP_MESSAGE
from clive.__private.core.constants.tui.navigation_bindings import PREVIOUS_SCREEN
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm


class Description(Static):
    """Description of the welcome screen."""


class WelcomeFormScreen(BaseScreen, CreateProfileFormScreen):
    BINDINGS = [
        Binding(
            SHOW_HELP.key, "help", "Help", id=SHOW_HELP.id
        ),  # help is a hidden global binding, but we want to show it here
        Binding(f"{PREVIOUS_SCREEN.key},escape", "_there_is_no_back", "Nothing", show=False, id=PREVIOUS_SCREEN.id),
    ]
    CSS_PATH = [get_relative_css_path(__file__)]
    SHOW_RAW_HEADER = True

    def __init__(self, owner: CreateProfileForm) -> None:
        super().__init__(owner)
        self._description = "Let's create profile!\n" + PRESS_HELP_MESSAGE

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
