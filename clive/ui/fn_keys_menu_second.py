from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.fn_keys_menu_component import FnKeysMenuComponent
from clive.ui.fn_keys_menu_first import FnKeysMenuFirst
from clive.ui.left_component import LeftComponentFirst

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.dashboard_component import DashboardComponent


class FnKeysMenuSecond(FnKeysMenuComponent):
    def __init__(self, parent: DashboardComponent) -> None:
        self.__parent = parent
        self.__parent.key_bindings.append(self._get_key_bindings())

        super().__init__()

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        self.__parent.left_component = LeftComponentFirst()
        self.__parent.menu_component = FnKeysMenuFirst(self.__parent)

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
