from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Input, Static

from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.command_secured import PasswordResultCallbackT


class ConfirmWithPassword(BaseScreen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("f2", "confirm", "Ok"),
    ]

    def __init__(self, result_callback: PasswordResultCallbackT, action_name: str = "") -> None:
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
        self.__result_callback("")
        self.app.pop_screen()

    def action_confirm(self) -> None:
        if not self.__validate_password():
            Notification("Invalid password", category="error").show()
            return

        self.__result_callback(self.__get_password_input())
        self.app.pop_screen()

    def __validate_password(self) -> bool:
        # TODO: Make a call to beekeeper to validate the password
        return True

    def __get_password_input(self) -> str:
        return self.__password_input.value
