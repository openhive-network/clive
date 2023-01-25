from __future__ import annotations

from typing import Any, Callable, List, Tuple

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import RadioList

from clive.ui.component import Component, T

ModelItemT = Tuple[Any, str]
ModelT = List[ModelItemT]


class RadioListWithModel(Component[T]):
    def __init__(self, parent: T, get_model: Callable[[], ModelT]) -> None:
        self.__get_model = get_model
        self.container: RadioList[ModelItemT]
        super().__init__(parent)

    @property
    def current_item(self) -> ModelItemT:
        return self.container.current_value

    def _create_container(self) -> AnyContainer:
        return RadioList(values=self.__get_model())
