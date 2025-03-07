from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.reactive import var

from clive.__private.core.constants.tui.bindings import NEXT_SCREEN_BINDING_KEY, PREVIOUS_SCREEN_BINDING_KEY
from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.forms.navigation_buttons import NextScreenButton, PreviousScreenButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from clive.__private.ui.forms.form import Form


BackScreenModes = Literal["back_to_unlock", "nothing_to_back", "back_to_previous"]


class FormScreenBase(CliveScreen, Contextual[ContextT]):
    def __init__(self, owner: Form[ContextT]) -> None:
        self._owner = owner
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self._owner.context


class FormScreen(FormScreenBase[ContextT], ABC):
    BINDINGS = [
        Binding("escape", "previous_screen", "Previous screen", show=False),
        Binding(NEXT_SCREEN_BINDING_KEY, "next_screen", "Next screen"),
    ]

    should_finish: bool = var(default=False)  # type: ignore[assignment]
    back_screen_mode: BackScreenModes = var("back_to_previous")  # type: ignore[assignment]

    class Finish(Message):
        """Used to determine that the form is finished."""

    @dataclass
    class ValidationSuccess:
        """Used to determine that form validation passed and next screen should be displayed."""

    @dataclass
    class ValidationFail:
        """Used to determine that form validation failed so next screen should not be displayed."""

        notification_message: str | None = None
        """Message to be displayed in the notification."""

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        if self.back_screen_mode == "nothing_to_back":
            return

        if self.back_screen_mode == "back_to_unlock":
            await self._back_to_unlock_screen()
            return

        self._owner.previous_screen()

    @on(NextScreenButton.Pressed)
    @on(CliveInput.Submitted)
    async def action_next_screen(self) -> None:
        if not self.is_step_optional():
            validation_result = await self.validate()
            if isinstance(validation_result, self.ValidationFail):
                notification_message = validation_result.notification_message
                if notification_message:
                    self.notify(notification_message, severity="error")
                return

            await self.apply()

        if self.should_finish:
            self.post_message(self.Finish())
            return

        self._owner.next_screen()

    @abstractmethod
    async def validate(self) -> ValidationFail | ValidationSuccess | None:
        """Validate the form. None is same as ValidationSuccess."""

    @abstractmethod
    async def apply(self) -> None:
        """Apply the form data."""

    def is_step_optional(self) -> bool:
        """Override to skip form validation."""
        return False

    def watch_back_screen_mode(self, value: BackScreenModes) -> None:
        """Responding to a change of the back screen mode."""
        if value == "nothing_to_back":
            self.unbind(PREVIOUS_SCREEN_BINDING_KEY)
            return

        self.bind(Binding(PREVIOUS_SCREEN_BINDING_KEY, "previous_screen", "Previous screen"))

    async def _back_to_unlock_screen(self) -> None:
        await self.app.switch_mode("unlock")
