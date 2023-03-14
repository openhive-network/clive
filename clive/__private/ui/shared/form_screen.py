from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.screen import Screen

if TYPE_CHECKING:
    from clive.__private.ui.shared.form import Form


class FormScreenBase(Screen):
    def __init__(self, owner: Form) -> None:
        self._owner = owner
        super().__init__()

class FirstFormScreen(FormScreenBase):
    BINDINGS = [
        Binding("ctrl+n", "next_screen", "Next screen"),
    ]

    def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase):
    BINDINGS = [
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()


class FormScreen(FirstFormScreen, LastFormScreen):
    pass
