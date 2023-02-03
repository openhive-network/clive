from __future__ import annotations

from typing import Callable, Generic, List, Optional, Tuple, TypeVar

from prompt_toolkit.layout import AnyContainer, HSplit, Window
from prompt_toolkit.widgets import Frame, RadioList

from clive.ui.component import Component, T

ItemT = TypeVar("ItemT")
ModelItemT = Tuple[Optional[ItemT], str]
ModelT = List[ModelItemT[ItemT]]


class RadioListWithModel(Generic[ItemT, T], Component[T]):
    def __init__(self, parent: T, get_model: Callable[[], ModelT[ItemT]]) -> None:
        self.__null_item = (None, "-- EMPTY LIST --")
        self.__radio: RadioList[Optional[ItemT]]
        self.__get_model = get_model
        super().__init__(parent)

    @property
    def current_item(self) -> Optional[ItemT]:
        return self.__radio.current_value

    @property
    def model(self) -> ModelT[ItemT]:
        proposed_model = self.__get_model()
        if len(proposed_model) == 0:
            return [self.__null_item]
        return proposed_model

    def __update_radio_list(self) -> RadioList[Optional[ItemT]]:
        self.__radio = RadioList(values=self.model)
        return self.__radio

    def _create_container(self) -> AnyContainer:
        return Frame(HSplit([self.__update_radio_list(), Window()]))
