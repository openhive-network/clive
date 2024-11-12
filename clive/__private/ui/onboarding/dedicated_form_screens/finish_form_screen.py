from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.contextual import ContextT
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.onboarding.form_screen import LastFormScreen
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.onboarding.form import Form


class Description(Static):
    """Some description text."""


class ButtonsContainer(Horizontal):
    """Container holding buttons."""


class FinishFormScreen(BaseScreen, LastFormScreen[ContextT]):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, owner: Form[ContextT], end_note: str) -> None:
        self.__end_note = end_note
        super().__init__(owner)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("done!"):
            yield Description(self.__end_note)
            with ButtonsContainer():
                yield CliveButton("Finish!", variant="success", id_="finish-button")
                yield CliveButton("Forgot something?", id_="forgot-button")

    @on(CliveButton.Pressed, "#forgot-button")
    async def previous_screen(self) -> None:
        await self.action_previous_screen()

    @on(CliveButton.Pressed, "#finish-button")
    async def finish(self) -> None:
        # Has to be done in a separate task to avoid deadlock. More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker(self.action_finish())

    async def action_finish(self) -> None:
        await self._owner.execute_post_actions()
        await self.app.switch_mode("dashboard")
        await self.app.remove_mode("onboarding")
        await self.app.remove_mode("unlock")
