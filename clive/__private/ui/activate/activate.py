from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Protocol

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.validation import Integer
from textual.widgets import Checkbox

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from textual.app import ComposeResult


class ActivationResultCallback(Protocol):
    def __call__(self, *, activated: bool) -> Awaitable[None]: ...


ActivationResultCallbackOptional = ActivationResultCallback | None


class ActiveModeTimeContainer(Horizontal):
    """Container for the active mode time switch and input."""


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class Activate(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("f2", "activate", "Ok"),
    ]

    def __init__(self, *, activation_result_callback: ActivationResultCallbackOptional = None) -> None:
        super().__init__()
        self._activation_result_callback = activation_result_callback
        self._name_input = LabelizedInput("Profile name", value=self.profile_data.name)
        self._password_input = TextInput("Password", password=True)
        self._permanent_active_mode_switch = Checkbox("Permanent active mode?")
        self._temporary_active_mode_input = IntegerInput(
            "Active mode time (minutes)",
            value=60,
            always_show_title=True,
            validators=[Integer(minimum=1)],
            id="active-mode-input",
        )

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer(section_title="Activate profile"):
            yield self._name_input
            yield self._password_input
            with ActiveModeTimeContainer():
                yield self._permanent_active_mode_switch
                yield self._temporary_active_mode_input
            with ButtonsContainer():
                yield CliveButton("Ok", variant="success", id_="activate-button")
                yield CliveButton("Cancel", variant="error", id_="cancel-button")

    @on(Checkbox.Changed)
    def toggle_active_mode_temporary_time(self) -> None:
        self._temporary_active_mode_input.toggle_class("-hidden")

    @on(CliveButton.Pressed, "#cancel-button")
    async def action_cancel(self) -> None:
        await self.__exit_cancel()

    @on(CliveButton.Pressed, "#activate-button")
    async def action_activate(self) -> None:
        permanent_active = self._permanent_active_mode_switch.value
        active_mode_time: timedelta | None = None

        if not permanent_active:
            if not CliveValidatedInput.validate_many(self._password_input, self._temporary_active_mode_input):
                # do not exit_cancel here, because we want to stay on the screen
                return

            active_mode_time = timedelta(minutes=self._temporary_active_mode_input.value_or_error)  # already validated

        password = self._password_input.value_or_none()
        if password is None:
            # do not exit_cancel here, because we want to stay on the screen
            return

        if not (
            await self.commands.activate(password=password, time=active_mode_time, permanent=permanent_active)
        ).success:
            # do not exit_cancel here, because we want to stay on the screen
            return

        await self.__exit_success()

    async def __exit_success(self) -> None:
        self.app.pop_screen()
        await self.__set_activation_result(value=True)

    async def __exit_cancel(self) -> None:
        self.app.pop_screen()
        await self.__set_activation_result(value=False)

    async def __set_activation_result(self, *, value: bool) -> None:
        if self._activation_result_callback is not None:
            await self._activation_result_callback(activated=value)
