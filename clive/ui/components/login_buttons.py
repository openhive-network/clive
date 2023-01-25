from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import Button

from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.view_switcher import switch_view

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent

    from clive.ui.views.login import Login


class LoginButtons(ButtonsMenu["Login"]):
    def __init__(self, parent: Login) -> None:
        super().__init__(parent)

    def _create_buttons(self) -> list[Button]:
        return [Button("F1 Log in", handler=self.__f1_action), Button("F2 Registration", handler=self.__f2_action)]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        return kb

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        logger.info(f"Login as: {self._parent.main_panel.profile_name}")
        switch_view("dashboard")

    @staticmethod
    def __f2_action(event: KeyPressEvent | None = None) -> None:
        switch_view("registration")
