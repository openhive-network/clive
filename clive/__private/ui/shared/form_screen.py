from __future__ import annotations

from typing import TYPE_CHECKING, Generic

from textual.binding import Binding
from textual.screen import Screen

from clive.ui.shared.form import ContextT

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


class FormScreenBase(Generic[ContextT], Screen):
    def __init__(self, owner: Form[ContextT]) -> None:
        self._owner = owner
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self._owner.context()


class FirstFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("ctrl+n", "next_screen", "Next screen"),
    ]

    def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()


class FormScreen(FirstFormScreen[ContextT], LastFormScreen[ContextT]):
    pass
