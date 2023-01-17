from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.fn_keys_menu_component import FnKeysMenuComponent
from clive.ui.left_component import LeftComponentSecond

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.dashboard_component import DashboardComponent


class FnKeysMenuFirst(FnKeysMenuComponent):
    def __init__(self, parent: DashboardComponent) -> None:
        self.__parent = parent

        super().__init__()

        self.__parent.key_bindings.append(self._key_bindings)

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        from clive.app import clive  # TODO: This is a hack. Find a better way to do this.

        clive.set_focus(self._buttons[-1])

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        from clive.ui.fn_keys_menu_second import FnKeysMenuSecond  # TODO: This is a hack. Find a better way to do this.

        self.__parent.key_bindings.remove(self._key_bindings)
        self.__parent.left_component = LeftComponentSecond()
        self.__parent.menu_component = FnKeysMenuSecond(self.__parent)

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
