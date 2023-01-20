from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.components.buttons_menu import ButtonsMenu

if TYPE_CHECKING:
    from clive.ui.views.form import Form  # noqa: F401


class FormButtons(ButtonsMenu["Form"]):
    def _create_buttons(self) -> list[Button]:
        return [
            Button("F1 Previous", handler=self.__f1_action),
            Button("F2 Next", handler=self.__f2_action),
            Button("F3 Cancel", handler=self.__f3_action),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        kb.add(Keys.F3)(self.__f3_action)

        return kb

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        self._parent.previous_view()

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        self._parent.next_view()

    def __f3_action(self, event: KeyPressEvent | None = None) -> None:
        self._parent.cancel()
