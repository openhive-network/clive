from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.dashboard.account_info import AccountInfo
from clive.ui.dashboard.buttons_menu_first import ButtonsMenuFirst

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.dashboard.dashboard import Dashboard


class ButtonsMenuSecond(ButtonsMenu["Dashboard"]):
    def __init__(self, parent: Dashboard) -> None:
        super().__init__(parent)
        self._parent.key_bindings.append(self._get_key_bindings())

    def __f2_action(self, _: KeyPressEvent | None = None) -> None:
        self._parent.main_panel = AccountInfo(self._parent)
        self._parent.buttons = ButtonsMenuFirst(self._parent)

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
