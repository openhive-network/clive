from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Dimension, HSplit, VSplit, WindowAlign
from prompt_toolkit.widgets import Box, Frame, Label, TextArea

from clive.ui.buttons_menu_first import ButtonsMenuFirst
from clive.ui.component import Component
from clive.ui.left_component import LeftComponentFirst
from clive.ui.view import DynamicView

if TYPE_CHECKING:
    from clive.ui.buttons_menu import ButtonsMenu


class Dashboard(DynamicView):
    def __init__(self) -> None:
        self.__key_bindings: list[KeyBindings] = []

        self.__left_component: Component = LeftComponentFirst()
        self.__right_component = self.__create_right_component()
        self.__prompt_component = self.__create_prompt_component()
        self.__menu_component: ButtonsMenu = ButtonsMenuFirst(self)
        super().__init__()

    @property
    def left_component(self) -> Component:
        return self.__left_component

    @left_component.setter
    def left_component(self, component: Component) -> None:
        self.__left_component = component

    @property
    def menu_component(self) -> Component:
        return self.__menu_component

    @menu_component.setter
    def menu_component(self, component: ButtonsMenu) -> None:
        self.__menu_component = component

    @property
    def key_bindings(self) -> list[KeyBindings]:
        return self.__key_bindings

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                Label(text=self.__welcome_message, align=WindowAlign.CENTER),
                Box(
                    HSplit(
                        [
                            VSplit(
                                [
                                    Frame(
                                        self.__left_component.container,
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
        return f"Hello from CLIVE! {time}"

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
