from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Input, Static

from clive.__private.core.commands.abc.command_secured import InvalidPasswordError
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult


PasswordResultCallbackType = Callable[[str], None]


class ConfirmWithPassword(BaseScreen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("f2", "confirm", "Ok"),
    ]

    def __init__(
        self,
        result_callback: PasswordResultCallbackType,
        action_name: str = "",
    ) -> None:
        self.__result_callback = result_callback
        self.__action_name = action_name
        self.__password_input = Input(placeholder="Password", password=True, id="password_input")
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Please enter your password to continue.", id="hint")
            if self.__action_name:
                yield Static(f"Action: {self.__action_name}", id="action")
            yield self.__password_input

    def action_cancel(self) -> None:
        self.app.pop_screen()
        self.__result_callback("")

    def action_confirm(self) -> None:
        with self.app.batch_update():
            self.app.pop_screen()

            try:
                self.__result_callback(self.__get_password_input())
            except InvalidPasswordError:
                self.app.push_screen(ConfirmWithPassword(self.__result_callback, self.__action_name))
                Notification("Invalid password", category="error").show()

    def __get_password_input(self) -> str:
        return self.__password_input.value
