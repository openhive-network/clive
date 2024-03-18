from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.storage.contextual import ContextT
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FirstFormScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class WelcomeTitle(Static):
    """Title of the welcome screen."""


class WelcomeFormScreen(BaseScreen, FirstFormScreen[ContextT]):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "pop_screen", "Back")]

    def __init__(self, owner: Form[ContextT], title: str) -> None:
        self.__title = title
        super().__init__(owner)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome"):
            yield WelcomeTitle(self.__title)
            yield CliveButton("Start!", variant="primary", id_="welcome_button_start")

    @on(CliveButton.Pressed, "#welcome_button_start")
    async def begin(self) -> None:
        await self.action_next_screen()
