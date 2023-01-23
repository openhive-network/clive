from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Generic, TypeVar

from prompt_toolkit.layout import HSplit, VSplit, WindowAlign
from prompt_toolkit.widgets import Frame, Label

from clive.abstract_class import AbstractClass
from clive.ui.view import View

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from clive.ui.component import Component  # noqa: F401
    from clive.ui.components.buttons_menu import ButtonsMenu  # noqa: F401


M = TypeVar("M", bound="Component[Any]")
B = TypeVar("B", bound="ButtonsMenu[Any]")


class ButtonsBased(View, Generic[M, B], AbstractClass):
    def __init__(self, main_panel: M, buttons: B) -> None:
        self.__main_panel = main_panel
        self.__buttons = buttons
        super().__init__()

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                VSplit(
                    [
                        Label(text=self.__welcome_message),
                        Label(text=f"View: {self.__class__.__name__}", align=WindowAlign.RIGHT),
                    ]
                ),
                self.__main_panel.container,
                Frame(self.__buttons.container, style="class:primary"),
            ],
            style="class:primary",
            key_bindings=self.__buttons.key_bindings,
        )

    @staticmethod
    def __welcome_message() -> str:
        time = datetime.now().strftime("%H:%M:%S")
        return f"Hello from CLIVE! {time}"

    @property
    def main_panel(self) -> M:
        return self.__main_panel

    @main_panel.setter
    def main_panel(self, value: M) -> None:
        self.__main_panel = value
        self._rebuild()

    @property
    def buttons(self) -> B:
        return self.__buttons

    @buttons.setter
    def buttons(self, value: B) -> None:
        self._set_buttons(value)

    def _set_buttons(self, value: B) -> None:
        self.__buttons = value
        self._rebuild()
