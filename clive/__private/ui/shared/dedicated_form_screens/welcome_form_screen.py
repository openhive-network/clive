from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.storage.contextual import ContextT
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FirstFormScreen
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class Description(Static):
    """Description of the welcome screen."""


class WelcomeFormScreen(BaseScreen, FirstFormScreen[ContextT]):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, owner: Form[ContextT], description: str) -> None:
        self.__description = description
        super().__init__(owner)

    def _content_after_description(self) -> ComposeResult:
        """Override this method to add content after title."""
        return []

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome"):
            yield Description(self.__description)
            yield from self._content_after_description()
            yield CliveButton("Start!", id_="welcome-button-start")

    @on(CliveButton.Pressed, "#welcome-button-start")
    async def begin(self) -> None:
        await self.action_next_screen()
