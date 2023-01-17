from datetime import datetime
from typing import Optional

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Dimension, HorizontalAlign, HSplit, VSplit, WindowAlign
from prompt_toolkit.widgets import Box, Button, Frame, Label, TextArea

from clive.ui.component import Component
from clive.ui.left_component import LeftComponentFirst


class DashboardComponent(Component):
    def __init__(self) -> None:
        self.__left_component: Component = LeftComponentFirst()
        self.__right_component = self.__create_right_component()
        self.__prompt_component = self.__create_prompt_component()
        self.__menu_component = self.__create_menu_component()
        super().__init__()

    @property
    def left_component(self) -> Component:
        return self.__left_component

    @left_component.setter
    def left_component(self, component: Component) -> None:
        self.__left_component = component

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
                                self.__menu_component,
                            ),
                        ]
                    ),
                    padding=1,
                ),
            ],
            style="class:primary",
            key_bindings=self.__get_key_bindings(),
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

    def __create_menu_component(self) -> VSplit:
        return VSplit(
            [
                Button(text="F1 First", handler=self.f1_action),
                Button(text="F2 Second"),
                Button(text="F3 Third"),
            ],
            align=HorizontalAlign.LEFT,
            padding=1,
        )

    def __get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.f1_action)
        return kb

    def f1_action(self, event: Optional[KeyPressEvent] = None) -> None:
        from clive.app import clive  # TODO: This is a hack. Find a better way to do this.

        clive.set_focus(self.__menu_component.children[-1])
