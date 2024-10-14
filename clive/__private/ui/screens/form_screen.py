from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.ui.clive_screen import CliveScreen
from clive.exceptions import FormValidationError

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
    async def action_next_screen(self) -> None:
        try:
            await self.apply_and_validate()
        except FormValidationError as e:
            self.validation_failure(e)
        else:
            await super().action_next_screen()

    def validation_failure(self, exception: FormValidationError) -> None:
        self.notify(f"Data validated with error, reason: {exception.reason}", severity="error")

    @abstractmethod
    async def apply_and_validate(self) -> None:
        """Perform its actions and raise FormValidationError if some input is invalid."""
