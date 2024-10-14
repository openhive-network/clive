from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.ui.clive_screen import CliveScreen

if TYPE_CHECKING:
    from clive.__private.ui.onboarding.form import Form


class FormScreenBase(CliveScreen, Contextual[ContextT]):
    def __init__(self, owner: Form[ContextT]) -> None:
        self._owner = owner
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self._owner.context


class FirstFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("ctrl+n", "next_screen", "Next screen"),
    ]

    async def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    async def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()


class FormScreen(FirstFormScreen[ContextT], LastFormScreen[ContextT], ABC):
    @dataclass
    class ValidationSuccess:
        """Used to determine that form validation passed and next screen should be displayed."""

    @dataclass
    class ValidationFail:
        """Used to determine that form validation failed so next screen should not be displayed."""

        notification_message: str | None = None
        """Message to be displayed in the notification."""

    async def action_next_screen(self) -> None:
        validation_result = await self.validate()
        if isinstance(validation_result, self.ValidationFail):
            notification_message = validation_result.notification_message
            if notification_message:
                self.notify(notification_message, severity="error")
            return

        await self.apply()
        await super().action_next_screen()

    @abstractmethod
    async def validate(self) -> ValidationFail | ValidationSuccess | None:
        """Validate the form. None is same as ValidationSuccess."""

    @abstractmethod
    async def apply(self) -> None:
        """Apply the form data."""
