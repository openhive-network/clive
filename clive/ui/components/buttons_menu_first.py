from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.app_status import app_status
from clive.ui.components.account_info import LeftComponentSecond
from clive.ui.components.buttons_menu import ButtonsMenu

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.views.dashboard import Dashboard


class ButtonsMenuFirst(ButtonsMenu["Dashboard"]):
    def __init__(self, parent: Dashboard) -> None:
        super().__init__(parent)

        self._parent.key_bindings.append(self._key_bindings)

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        app_status.deactivate() if app_status.active_mode else app_status.activate()
        self._rebuild()

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        from clive.ui.components.buttons_menu_second import ButtonsMenuSecond

        if self._key_bindings in self._parent.key_bindings:
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
            Button(text=f"F1 {self.__switch_mode_text()}", handler=self.__f1_action),
            Button(text="F2 SecondComponent", handler=self.__f2_action),
            Button(text="F3 Do nothing"),
        ]

    @staticmethod
    def __switch_mode_text() -> str:
        return "Deactivate" if app_status.active_mode else "Activate"
