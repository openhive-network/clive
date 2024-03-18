from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.exceptions import CommunicationError

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
        self._password_input = TextInput("Password", password=True)
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

        if not await self._is_password_valid(password):
            self.notify("Invalid password", severity="error")
            return

        with self.app.batch_update():
            self.app.pop_screen()
            await self.__result_callback(password)

    async def _is_password_valid(self, password: str) -> bool:
        """
        Check if the password is valid.

        I know this is a hack, but currently seems like the only way to check if the password is valid.
        CLive does not store the password in the memory/on the disk, we always use the beekeeper API on the fly when
        password is required. In this situation we need to check if the password is valid, without taking any action
        on the wallet.

        The only API's that we could use to check if the password is valid are:
        - unlock
        - remove_key

        and since unlock is changing the state of the wallet, only remove_key is left.
        """
        invalid_public_key = "not-existing"
        invalid_password_message = "Invalid password for wallet"
        wrong_public_key_message = f"Parse Error:Unable to decode base58 string {invalid_public_key}"

        try:
            await self.app.world.beekeeper.api.remove_key(
                wallet_name=self.app.world.profile_data.name,
                password=password,
                public_key=invalid_public_key,
            )
        except CommunicationError as error:
            if invalid_password_message in str(error):
                return False
            if wrong_public_key_message in str(error):
                # that means that the password is valid, but the public key is invalid
                return True

        raise RuntimeError("Beekeeper error format has changed! Cannot check if the password is valid.")
