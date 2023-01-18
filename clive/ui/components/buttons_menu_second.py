from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.buttons_menu_first import ButtonsMenuFirst
from clive.ui.components.left_component import LeftComponentFirst

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent



class ButtonsMenuSecond(ButtonsMenu):
    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        self._context.left_component = LeftComponentFirst()
        self._context.menu_component = ButtonsMenuFirst()
        self._context.menu_component.context = self._context

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F2)(self.__f2_action)

        return kb

    def _create_buttons(self) -> list[Button]:
        return [
            Button(text="F1 Do nothing"),
            Button(text="F2 First Component", handler=self.__f2_action),
            Button(text="F3 Do nothing"),
        ]
