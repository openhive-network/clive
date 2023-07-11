from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.storage.contextual import ContextT, Contextual
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


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

    def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("escape", "start_over", "Cancel"),
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()

    def action_start_over(self) -> None:
        self._owner.reset()


class FormScreen(FirstFormScreen[ContextT], LastFormScreen[ContextT], ABC):
    def action_next_screen(self) -> None:
        try:
            self.apply_and_validate()
        except FormValidationError as e:
            self.validation_failure(e)
        else:
            super().action_next_screen()
            self.validation_success()

    def validation_failure(self, exception: FormValidationError) -> None:
        Notification(f"Data validated with error, reason: {exception.reason}", category="error").show()

    def validation_success(self) -> None:
        Notification("Data validated successfully", category="success").show()

    @abstractmethod
    def apply_and_validate(self) -> None:
        """Should perform its actions and raise FormValidationError if some input is invalid."""
