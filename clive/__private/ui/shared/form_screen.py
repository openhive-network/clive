from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.storage.contextual import ContextT, Contextual
from clive.ui.widgets.clive_screen import CliveScreen

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


class FormScreenBase(CliveScreen, Contextual[ContextT]):
    def __init__(self, owner: Form[ContextT]) -> None:
        self._owner = owner
        super().__init__()

    def get_context(self) -> ContextT:
        return self._owner.context


class FirstFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("ctrl+n", "next_screen", "Next screen"),
    ]

    def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("esc", "start_over", "Cancel"),
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()

    def action_start_over(self) -> None:
        self._owner.reset()


class FormScreen(FirstFormScreen[ContextT], LastFormScreen[ContextT]):
    pass
