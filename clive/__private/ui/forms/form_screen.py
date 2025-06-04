from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.reactive import var

from clive.__private.core.constants.tui.bindings import NEXT_SCREEN_BINDING_KEY, PREVIOUS_SCREEN_BINDING_KEY
from clive.__private.core.contextual import Contextual
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.forms.form_context import FormContextT
from clive.__private.ui.forms.navigation_buttons import NextScreenButton, PreviousScreenButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from clive.__private.ui.forms.form import Form


class FormScreen(CliveScreen, Contextual[FormContextT]):
    BINDINGS = [
        Binding(
            f"{PREVIOUS_SCREEN_BINDING_KEY},escape",
            "previous_screen",
            "Previous screen",
            key_display="^p",
        ),
        Binding(NEXT_SCREEN_BINDING_KEY, "next_screen", "Next screen"),
    ]

    _should_finish: bool = var(default=False, init=False)  # type: ignore[assignment]

    @dataclass
    class ValidationSuccess:
        """Used to determine that form validation passed and next screen should be displayed."""

    @dataclass
    class ValidationFail:
        """Used to determine that form validation failed so next screen should not be displayed."""

        notification_message: str | None = None
        """Message to be displayed in the notification."""

    def __init__(self, owner: Form[FormContextT]) -> None:
        self._owner = owner
        super().__init__()

    @property
    def owner(self) -> Form[FormContextT]:
        return self._owner

    @property
    def context(self) -> FormContextT:
        return self.owner.context

    @property
    def should_finish(self) -> bool:
        return self._should_finish

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        await self.owner.previous_screen()

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

        await self.owner.next_screen()

    @abstractmethod
    async def validate(self) -> ValidationFail | ValidationSuccess | None:
        """Validate the form. None is same as ValidationSuccess."""

    @abstractmethod
    async def apply(self) -> None:
        """Apply the form data."""

    def is_step_optional(self) -> bool:
        """Override to skip form validation."""
        return False
