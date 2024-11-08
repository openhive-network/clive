from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.password_input import PasswordInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConfirmWithPassword(BaseScreen[str]):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("f2", "confirm", "Ok"),
    ]

    def __init__(
        self,
        title: str = "",
    ) -> None:
        self._password_input = PasswordInput()
        self._title = title
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer(section_title=self._title):
            yield Static("Please enter your password to continue.", id="hint")
            yield self._password_input

    def action_cancel(self) -> None:
        self.dismiss()

    async def action_confirm(self) -> None:
        password = self._password_input.value_or_none()
        if password is None:
            return

        if not await self._is_password_valid(password):
            self.notify("Invalid password", severity="error")
            return

        with self.app.batch_update():
            await self.dismiss(password)

    async def _is_password_valid(self, password: str) -> bool:
        wrapper = await self.commands.is_password_valid(password=password)
        if not wrapper.success:
            return False
        return wrapper.result_or_raise
