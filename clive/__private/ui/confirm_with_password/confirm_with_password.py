from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.widgets import Input, Static

from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.abc.command_observable import SenderT
    from clive.__private.core.commands.abc.command_secured import CommandSecured


class ConfirmWithPassword(BaseScreen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("f2", "confirm", "Ok"),
    ]

    def __init__(self, confirmed_command: CommandSecured[Any]) -> None:
        self.__confirmed_command = confirmed_command
        self.__password_input = Input(placeholder="Password", password=True, id="password_input")
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Please enter your password to continue.", id="hint")
            if action_name := self.__confirmed_command.action_name:
                yield Static(f"Action: {action_name}", id="action")
            yield self.__password_input

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def action_confirm(self) -> None:
        if not self.__validate_password():
            Notification("Invalid password", category="error").show()
            return

        self.__confirmed_command.observe_result(self.__on_confirmation_result)
        self.__confirmed_command.arm(password=self.__get_password_input())
        self.app.pop_screen()
        self.__confirmed_command.fire()

    def __on_confirmation_result(self, _: SenderT, __: Any | None, exception: Exception | None) -> None:  # noqa: ARG002
        Notification(
            f"Password is correct. Action: `{self.__confirmed_command.action_name}` succeeded.", category="success"
        ).show()

    def __validate_password(self) -> bool:
        # TODO: Make a call to beekeeper to validate the password
        return True

    def __get_password_input(self) -> str:
        return self.__password_input.value
