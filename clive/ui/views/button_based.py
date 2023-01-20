from __future__ import annotations

from abc import ABC

from prompt_toolkit.layout import HSplit
from prompt_toolkit.widgets import Frame

from clive.ui.component import Component
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.view import View
from clive.ui.view_manager import view_manager


class ButtonsBased(View, ABC):
    def __init__(self, main_pane: Component, buttons: ButtonsMenu) -> None:
        self.__main_pane = main_pane
        self.__buttons = buttons
        super().__init__(view_manager)

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                Frame(self.__main_pane.container),
                Frame(self.__buttons.container, style="class:primary"),
            ],
            style="class:primary",
            key_bindings=self.__buttons.key_bindings,
        )

    @property
    def main_pane(self) -> Component:
        return self.__main_pane

    @main_pane.setter
    def main_pane(self, value: Component) -> None:
        self.__main_pane = value
        self._rebuild()

    @property
    def buttons(self) -> ButtonsMenu:
        return self.__buttons
