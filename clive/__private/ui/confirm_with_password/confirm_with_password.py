from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Static

from clive.__private.core.commands.abc.command_secured import InvalidPasswordError
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
        action_name: str = "",
    ) -> None:
        self.__result_callback = result_callback
        self.__action_name = action_name
        self._password_input = TextInput("Password", password=True, id="password_input")
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Please enter your password to continue.", id="hint")
            if self.__action_name:
                yield Static(f"Action: {self.__action_name}", id="action")
            yield self._password_input

    async def action_cancel(self) -> None:
        self.app.pop_screen()
        await self.__result_callback("")

    async def action_confirm(self) -> None:
        password = self._password_input.value_or_none()
        if password is None:
            return

        with self.app.batch_update():
            self.app.pop_screen()

            try:
                await self.__result_callback(password)
            except InvalidPasswordError:
                self.app.push_screen(ConfirmWithPassword(self.__result_callback, self.__action_name))
                self.notify("Invalid password", severity="error")
