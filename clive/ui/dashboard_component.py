from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, TypeVar

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Dimension, HSplit, VSplit, WindowAlign
from prompt_toolkit.widgets import Box, Frame, Label, TextArea

from clive.ui.component import Component
from clive.ui.fn_keys_menu_first import FnKeysMenuFirst
from clive.ui.left_component import LeftComponentFirst

if TYPE_CHECKING:
    from clive.ui.fn_keys_menu_component import FnKeysMenuComponent

T = TypeVar("T")
V = TypeVar("V")


class RegisteredComponentDescriptor:
    def __set_name__(self, owner, name: str) -> None:
        self.name = f"_REGISTERED__{name}"

    def __get__(self, instance: Optional[T], owner: Type[T]) -> V:  # type: ignore
        if instance is None:
            return self
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        registered_component = getattr(instance, "_registered_components")
        try:
            att = getattr(instance, self.name)
            if att in registered_component:
                registered_component.remove(att)
        except AttributeError:
            pass

        registered_component.append(value)
        setattr(instance, self.name, value)

    def __delete__(self, instance) -> None:
        delattr(instance, self.name)


class DashboardComponent(Component):
    left_component = RegisteredComponentDescriptor()

    def __init__(self) -> None:
        self._registered_components = []
        self.__key_bindings: list[KeyBindings] = []

        self.left_component: Component = LeftComponentFirst()
        self.__right_component = self.__create_right_component()
        self.__prompt_component = self.__create_prompt_component()
        self.__menu_component: FnKeysMenuComponent = FnKeysMenuFirst(self)

        super().__init__()

        self.register_component(self.__menu_component)
        # self.register_component(self.__left_component)

    # @property
    # def left_component(self) -> Component:
    #     return self.__left_component
    #
    # @left_component.setter
    # def left_component(self, component: Component) -> None:
    #     self._registered_components.remove(self.__left_component)
    #     self.__left_component = self.register_component(component)
    #
    @property
    def menu_component(self) -> Component:
        return self.__menu_component

    @menu_component.setter
    def menu_component(self, component: FnKeysMenuComponent) -> None:
        self._registered_components.remove(self.__menu_component)
        self.__menu_component = self.register_component(component)

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
