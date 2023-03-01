from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.dom import DOMNode

if TYPE_CHECKING:
    from clive.ui.shared.form import Form


class FormScreen(DOMNode):
    BINDINGS = [
        Binding("ctrl+p", "previous_screen", "Previous screen"),
        Binding("ctrl+n", "next_screen", "Next screen"),
    ]

    def set_form_owner(self, owner: "Form") -> FormScreen:
        self._owner = owner
        return self

    def __is_owner_set(self) -> bool:
        return hasattr(self, "_owner") and self._owner is not None

    def action_next_screen(self) -> None:
        assert self.__is_owner_set()
        self._owner.action_next_screen()

    def action_previous_screen(self) -> None:
        assert self.__is_owner_set()
        self._owner.action_previous_screen()
