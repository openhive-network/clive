from __future__ import annotations

from collections.abc import Callable, Coroutine
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Checkbox, Input, Static

from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


ActivationResultCallbackT = Callable[[bool], Coroutine[Any, Any, None]]
ActivationResultCallbackOptionalT = ActivationResultCallbackT | None


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class Activate(BaseScreen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("f2", "activate", "Ok"),
    ]

    class Succeeded(Message):
        """Emitted when application goes into the active state."""

    def __init__(self, *, activation_result_callback: ActivationResultCallbackOptionalT = None) -> None:
        super().__init__()
        self.__activation_result_callback = activation_result_callback
        self.__password_input = Input(placeholder="Password", password=True)
        self.__permanent_active_mode_switch = Checkbox("Permanent active mode")
        self.__temporary_active_mode_label = Static("Active mode time (minutes)", classes="label")
        self.__temporary_active_mode_input = Input("60", placeholder="Time in minutes", id="active-mode-input")

    def on_mount(self) -> None:
        self.__password_input.focus()

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Profile name", classes="label")
            yield Input(self.app.world.profile_data.name, disabled=True)
            yield Static("Password", classes="label", id="password-label")
            yield self.__password_input
            yield self.__permanent_active_mode_switch
            yield self.__temporary_active_mode_label
            yield self.__temporary_active_mode_input
            yield Static()
            with ButtonsContainer():
                yield CliveButton("Ok", variant="primary", id_="activate-button")
                yield CliveButton("Cancel", variant="error", id_="cancel-button")

    @on(Checkbox.Changed)
    def toggle_active_mode_temporary_time(self) -> None:
        self.__temporary_active_mode_label.toggle_class("-hidden")
        self.__temporary_active_mode_input.toggle_class("-hidden")

    @on(CliveButton.Pressed, "#cancel-button")
    async def action_cancel(self) -> None:
        await self.__exit_cancel()

    @on(CliveButton.Pressed, "#activate-button")
    async def action_activate(self) -> None:
        permanent_active = self.__permanent_active_mode_switch.value
        active_mode_time: timedelta | None = None

        if not permanent_active:
            raw_active_mode_time = self.__get_active_mode_time()
            if raw_active_mode_time is None:
                self.notify("The active mode time must be a number and >= 1", severity="error")
                return

            active_mode_time = timedelta(minutes=raw_active_mode_time)

        if not (
            await self.app.world.commands.activate(password=self.__password_input.value, time=active_mode_time)
        ).success:
            return

        await self.__exit_success()

    async def __exit_success(self) -> None:
        self.app.post_message_to_everyone(self.Succeeded())
        self.app.pop_screen()
        await self.__set_activation_result(True)

    async def __exit_cancel(self) -> None:
        self.app.pop_screen()
        await self.__set_activation_result(False)

    async def __set_activation_result(self, value: bool) -> None:
        if self.__activation_result_callback is not None:
            await self.__activation_result_callback(value)

    def __get_active_mode_time(self) -> int | None:
        try:
            value = int(self.__temporary_active_mode_input.value)
        except ValueError:
            return None
        else:
            return value if value >= 1 else None
