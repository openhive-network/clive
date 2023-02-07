from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Dimension, Float, HorizontalAlign, HSplit, VSplit
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from clive.ui.containerable import Containerable
from clive.ui.enums import ZIndex
from clive.ui.focus import set_focus
from clive.ui.get_view_manager import get_view_manager


class BaseFloat(Containerable[Float], ABC):
    """
    By deriving from this class you can create float which
    will be automatically visible after creation
    """

    def __init__(self, title: str, labels_with_inputs: Dict[str, TextArea]) -> None:
        self.__close_callback: Callable[[], None] = lambda: None
        self.__title = title
        self.__labels_n_inputs = labels_with_inputs
        super().__init__()
        get_view_manager().floats.float = self
        set_focus(self.container.content)

    def __close(self) -> None:
        get_view_manager().floats.float = None
        self.close_callback()

    def __cancel(self, _: KeyPressEvent | None = None) -> None:
        self._cancel()
        self.__close()

    def __ok(self, _: KeyPressEvent | None = None) -> None:
        if self._ok():
            self.__cancel()

    def _create_binding(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__ok)
        kb.add(Keys.F2)(self.__cancel)
        return kb

    @property
    def close_callback(self) -> Callable[[], None]:
        return self.__close_callback

    @close_callback.setter
    def close_callback(self, value: Callable[[], None]) -> None:
        self.__close_callback = value

    def _create_container(self) -> Float:
        return Float(
            Frame(
                HSplit(
                    [
                        VSplit(
                            [
                                HSplit([self.__create_label(key) for key in self.__labels_n_inputs]),
                                HSplit([self.__create_text_area(value) for value in self.__labels_n_inputs.values()]),
                            ]
                        ),
                        VSplit(
                            [
                                self.__create_popup_button("<F1> Ok", handler=self.__ok),
                                self.__create_popup_button("<F2> Cancel", handler=self.__cancel),
                            ],
                            align=HorizontalAlign.CENTER,
                            padding=Dimension(min=1),
                        ),
                    ]
                ),
                title=self.__title,
                key_bindings=self._create_binding(),
                modal=True,
            ),
            z_index=ZIndex.BASE_FLOAT,
        )

    def __create_popup_button(self, label: str, handler: Callable[[], None]) -> Button:
        return Button(label, handler, left_symbol="", right_symbol="", width=len(label))

    def _create_text_area(self, text: str = "") -> TextArea:
        return TextArea(text=text, multiline=False, width=Dimension(min=15))

    def __create_text_area(self, text_area: TextArea) -> Frame:
        return Frame(text_area)

    def __create_label(self, text: str) -> Frame:
        return Frame(Label(text=text))

    def _cancel(self) -> None:
        """Called when user clicks Cancel button"""

    @abstractmethod
    def _ok(self) -> bool:
        """Called when user clicks Ok button

        Returns:
            bool: True: closes window, False: keep window alive
        """
