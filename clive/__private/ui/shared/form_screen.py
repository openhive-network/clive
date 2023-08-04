from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.storage.contextual import ContextT, Contextual
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


class FormScreenBase(CliveScreen[None], Contextual[ContextT]):
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
        Binding("escape", "start_over", "Cancel"),
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    async def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()

    def action_start_over(self) -> None:
        self._owner.reset()


class FormScreen(FirstFormScreen[ContextT], LastFormScreen[ContextT], ABC):
    async def action_next_screen(self) -> None:
        try:
            await self.apply_and_validate()
        except FormValidationError as e:
            self.validation_failure(e)
        else:
            await super().action_next_screen()
            self.validation_success()

    def validation_failure(self, exception: FormValidationError) -> None:
        self.notify(f"Data validated with error, reason: {exception.reason}", severity="error")

    def validation_success(self) -> None:
        self.notify("Data validated successfully")

    @abstractmethod
    async def apply_and_validate(self) -> None:
        """Should perform its actions and raise FormValidationError if some input is invalid."""
