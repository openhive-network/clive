from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Protocol

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.validation import Integer
from textual.widgets import Checkbox

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from textual.app import ComposeResult


class UnlockResultCallback(Protocol):
    def __call__(self, *, unlocked: bool) -> Awaitable[None]: ...


UnlockResultCallbackOptional = UnlockResultCallback | None


class UnlockModeTimeContainer(Horizontal):
    """Container for the unlock mode time switch and input."""


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class Unlock(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("f2", "unlock", "Unlock wallet"),
    ]

    def __init__(self, *, unlock_result_callback: UnlockResultCallbackOptional = None) -> None:
        super().__init__()
        self._unlock_result_callback = unlock_result_callback
        self._name_input = LabelizedInput("Profile name", value=self.profile.name)
        self._password_input = TextInput("Password", password=True)
        self._permanent_unlock_switch = Checkbox("Permanent unlock?", value=True)
        self._temporary_unlock_input = IntegerInput(
            "Unlock time (minutes)",
            value=60,
            always_show_title=True,
            validators=[Integer(minimum=1)],
            id="unlock-mode-input",
            classes="-hidden",
        )

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer(section_title="Unlock wallet"):
            yield self._name_input
            yield self._password_input
            with UnlockModeTimeContainer():
                yield self._permanent_unlock_switch
                yield self._temporary_unlock_input
            with ButtonsContainer():
                yield CliveButton("Unlock", variant="success", id_="unlock-button")
                yield CliveButton("Cancel", variant="error", id_="cancel-button")

    @on(Checkbox.Changed)
    def toggle_unlock_temporary_time(self) -> None:
        self._temporary_unlock_input.toggle_class("-hidden")

    @on(CliveButton.Pressed, "#cancel-button")
    async def action_cancel(self) -> None:
        await self.__exit_cancel()

    @on(CliveButton.Pressed, "#unlock-button")
    async def action_unlock(self) -> None:
        permanent_unlock = self._permanent_unlock_switch.value
        unlocked_mode_time: timedelta | None = None

        if not permanent_unlock:
            if not CliveValidatedInput.validate_many(self._password_input, self._temporary_unlock_input):
                # do not exit_cancel here, because we want to stay on the screen
                return

            unlocked_mode_time = timedelta(minutes=self._temporary_unlock_input.value_or_error)  # already validated

        password = self._password_input.value_or_none()
        if password is None:
            # do not exit_cancel here, because we want to stay on the screen
            return

        if not (
            await self.commands.unlock(password=password, time=unlocked_mode_time, permanent=permanent_unlock)
        ).success:
            # do not exit_cancel here, because we want to stay on the screen
            return

        await self.__exit_success()

    async def __exit_success(self) -> None:
        self.app.pop_screen()
        await self.__set_unlock_result(value=True)

    async def __exit_cancel(self) -> None:
        self.app.pop_screen()
        await self.__set_unlock_result(value=False)

    async def __set_unlock_result(self, *, value: bool) -> None:
        if self._unlock_result_callback is not None:
            await self._unlock_result_callback(unlocked=value)
