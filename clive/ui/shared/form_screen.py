from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Union

from textual.binding import Binding

from clive.ui.shared.base_screen import BaseScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.ui.shared.form import Form


def _create_form_screen_bindings(show: bool) -> List[Union[Binding, Tuple[str, str, str]]]:
    return [
        Binding("p", "previous_screen", "Previous screen", show=show),
        Binding("n", "next_screen", "Next screen", show=show),
    ]


class FormScreen(BaseScreen):
    class Error(NotImplementedError):
        pass

    BINDINGS = _create_form_screen_bindings(False)

    def set_form_owner(self, owner: "Form") -> FormScreen:
        self._owner = owner
        for bind in _create_form_screen_bindings(True):
            if isinstance(bind, Binding):
                self._bindings.keys[bind.key] = bind
        return self

    def is_form(self) -> bool:
        return hasattr(self, "_owner") and self._owner is not None

    def action_next_screen(self) -> None:
        if self.is_form():
            self._owner.action_next_screen()

    def action_previous_screen(self) -> None:
        if self.is_form():
            self._owner.action_previous_screen()

    def create_form_panel(self) -> ComposeResult:
        raise FormScreen.Error()

    def _create_main_panel(self) -> ComposeResult:
        try:
            yield from self.create_form_panel()
        except FormScreen.Error:
            yield from super()._create_main_panel()
