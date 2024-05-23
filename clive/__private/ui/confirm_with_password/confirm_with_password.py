from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


PasswordResultCallbackType = Callable[[str], Awaitable[None]]


class ConfirmWithPassword(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("f2", "confirm", "Ok"),
    ]

    def __init__(
        self,
        result_callback: PasswordResultCallbackType,
        title: str = "",
    ) -> None:
        self.__result_callback = result_callback
        self._password_input = TextInput("Password", password=True)
        self._title = title
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer(section_title=self._title):
            yield Static("Please enter your password to continue.", id="hint")
            yield self._password_input

    async def action_cancel(self) -> None:
        self.app.pop_screen()
        await self.__result_callback("")

    async def action_confirm(self) -> None:
        password = self._password_input.value_or_none()
        if password is None:
            return

        if not await self._is_password_valid(password):
            self.notify("Invalid password", severity="error")
            return

        with self.app.batch_update():
            self.app.pop_screen()
            await self.__result_callback(password)

    async def _is_password_valid(self, password: str) -> bool:
        wrapper = await self.app.world.commands.is_password_valid(password=password)
        if not wrapper.success:
            return False
        return wrapper.result_or_raise
