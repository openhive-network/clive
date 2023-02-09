from __future__ import annotations

from typing import Callable, Generic, List, Tuple, TypeVar

from prompt_toolkit.layout import AnyContainer, HSplit, Window
from prompt_toolkit.widgets import Frame, RadioList

from clive.ui.component import Component, T

ItemT = TypeVar("ItemT")
ModelItemT = Tuple[ItemT, str]
ModelT = List[ModelItemT[ItemT]]


class RadioListWithModel(Generic[ItemT, T], Component[T]):
    def __init__(self, parent: T, get_model: Callable[[], ModelT[ItemT]]) -> None:
        self.__radio: RadioList[ItemT]
        self.__get_model = get_model
        super().__init__(parent)

    @property
    def current_item(self) -> ItemT:
        return self.__radio.current_value

    @property
    def model(self) -> ModelT[ItemT]:
        return self.__get_model()

    def __update_radio_list(self) -> RadioList[ItemT]:
        self.__radio = RadioList(values=self.model)
        return self.__radio

    def _create_container(self) -> AnyContainer:
        return Frame(HSplit([self.__update_radio_list(), Window()]))
