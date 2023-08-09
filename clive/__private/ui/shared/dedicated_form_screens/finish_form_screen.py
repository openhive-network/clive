from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Static

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
    """Some description text."""


class ButtonsContainer(Horizontal):
    """Container holding buttons."""


class FinishFormScreen(BaseScreen, LastFormScreen[ContextT]):
    BINDINGS = [Binding("f10", "finish", "Ok")]

    def __init__(self, owner: Form[ContextT], end_note: str) -> None:
        self.__end_note = end_note
        super().__init__(owner)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("done!"):
            yield Description(self.__end_note)
            with ButtonsContainer():
                yield CliveButton("Finish!", id_="finish-button")
                yield CliveButton("Forgot something?", id_="forgot-button")

    @on(CliveButton.Pressed, "#forgot-button")
    async def previous_screen(self) -> None:
        await self.action_previous_screen()

    @on(CliveButton.Pressed, "#finish-button")
    async def finish(self) -> None:
        await self.action_finish()

    async def action_finish(self) -> None:
        await self._owner.execute_post_actions()
        self.app.pop_screen_until(WelcomeFormScreen)

        # switch WelcomeFormScreen to the proper Dashboard screen
        if await self.app.world.app_state.is_active:
            self.app.switch_screen("dashboard_active")
        else:
            self.app.switch_screen("dashboard_inactive")
