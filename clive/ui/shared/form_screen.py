from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.dom import DOMNode

if TYPE_CHECKING:
    from clive.ui.shared.form import Form


class FormScreenBase(DOMNode):
    def set_form_owner(self, owner: "Form") -> FormScreenBase:
        self._owner = owner
        return self

    def _is_owner_set(self) -> bool:
        return hasattr(self, "_owner") and self._owner is not None


class FirstFormScreen(FormScreenBase):
    BINDINGS = [
        Binding("ctrl+n", "next_screen", "Next screen"),
    ]

    def action_next_screen(self) -> None:
        assert self._is_owner_set()
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase):
    BINDINGS = [
        Binding("ctrl+p", "previous_screen", "Previous screen"),
    ]

    def action_previous_screen(self) -> None:
        assert self._is_owner_set()
        self._owner.action_previous_screen()


class FormScreen(FirstFormScreen, LastFormScreen):
    pass
