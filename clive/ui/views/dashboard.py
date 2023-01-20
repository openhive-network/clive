from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Dimension, HSplit, VSplit, WindowAlign, AnyContainer
from prompt_toolkit.widgets import Box, Frame, Label, TextArea

from clive.ui.component import Component
from clive.ui.components.buttons_menu_first import ButtonsMenuFirst
from clive.ui.components.left_component import LeftComponentFirst
from clive.ui.view import ReadyView
from clive.ui.view_manager import ViewManager

if TYPE_CHECKING:
    from clive.ui.components.buttons_menu import ButtonsMenu


class Dashboard(ReadyView):
    def __init__(self, parent: ViewManager) -> None:
        self.__key_bindings: list[KeyBindings] = []

        self.__left_component: Component[Dashboard] = LeftComponentFirst(self)
        self.__right_component = self.__create_right_component()
        self.__prompt_component = self.__create_prompt_component()
        self.__menu_component: ButtonsMenu[Dashboard] = ButtonsMenuFirst(self)
        super().__init__(parent)

    @property
    def left_component(self) -> Component[Dashboard]:
        return self.__left_component

    @left_component.setter
    def left_component(self, component: Component[Dashboard]) -> None:
        self.__left_component = component

    @property
    def menu_component(self) -> Component[Dashboard]:
        return self.__menu_component

    @menu_component.setter
    def menu_component(self, component: ButtonsMenu[Dashboard]) -> None:
        self.__menu_component = component

    @property
    def key_bindings(self) -> list[KeyBindings]:
        return self.__key_bindings

    def _create_container(self) -> AnyContainer:
        return HSplit(
            [
                Label(text=self.__welcome_message, align=WindowAlign.CENTER),
                Box(
                    HSplit(
                        [
                            VSplit(
                                [
                                    Frame(
                                        self.left_component.container,
                                        width=Dimension(weight=3),
                                    ),
                                    Frame(
                                        self.__right_component,
                                    ),
                                ]
                            ),
                            self.__prompt_component,
                            Frame(
                                self.__menu_component.container,
                            ),
                        ]
                    ),
                    padding=1,
                ),
            ],
            style="class:primary",
            key_bindings=merge_key_bindings(self.__key_bindings),
        )

    @staticmethod
    def __welcome_message() -> str:
        time = datetime.now().strftime("%H:%M:%S")
        return "Hello from CLIVE! %s" % time

    @staticmethod
    def __create_right_component() -> TextArea:
        return TextArea(
            text="RIGHT COMPONENT",
            style="class:primary",
            focus_on_click=True,
        )

    @staticmethod
    def __create_prompt_component() -> TextArea:
        return TextArea(
            text="PROMPT COMPONENT",
            height=3,
            style="bg:#000000 #ffffff",
            focus_on_click=True,
        )
