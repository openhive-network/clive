from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.get_clive import get_clive
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.components.left_component import LeftComponentSecond
from clive.ui.focus import set_focus

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.views.dashboard import Dashboard


class ButtonsMenuFirst(ButtonsMenu["Dashboard"]):
    def __init__(self, parent: Dashboard) -> None:
        super().__init__(parent)

        self._parent.key_bindings.append(self._key_bindings)

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        set_focus(self._buttons[-1])

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        from clive.ui.components.buttons_menu_second import ButtonsMenuSecond

        get_clive().skip_focusing_menu()
        self._parent.key_bindings.remove(self._key_bindings)
        self._parent.main_panel = LeftComponentSecond(self._parent)
        self._parent.buttons = ButtonsMenuSecond(self._parent)

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
