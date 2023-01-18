from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.left_component import LeftComponentSecond
from clive.ui.focus import set_focus

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.views.dashboard import Dashboard


class ButtonsMenuFirst(ButtonsMenu):
    def __init__(self) -> None:
        super().__init__()

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        set_focus(self._buttons[-1])

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        from clive.ui.components.buttons_menu_second import (  # TODO: This is a hack. Find a better way to do this.
            ButtonsMenuSecond,
        )

        self._context.key_bindings.remove(self._key_bindings)
        self._context.left_component = LeftComponentSecond()
        self._context.menu_component = ButtonsMenuSecond()
        self._context.menu_component.context = self._context

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)

        return kb

    def _create_buttons(self) -> list[Button]:
        return [
            Button(text="F1 Select F3", handler=self.__f1_action),
            Button(text="F2 SecondComponent", handler=self.__f2_action),
            Button(text="F3 Do nothing"),
        ]
