from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import Float

from clive.ui.focus import set_focus
from clive.ui.get_view_manager import get_view_manager
from clive.ui.parented import Parented
from clive.ui.prompt_float import PromptFloat

if TYPE_CHECKING:
    from clive.ui.base_float import BaseFloat
    from clive.ui.catch import ErrorFloat
    from clive.ui.view_manager import ViewManager


class Floats(Parented["ViewManager"]):
    def __init__(self, parent: ViewManager) -> None:
        super().__init__(parent)

        self.__float: BaseFloat | None = None
        self.__error_float: ErrorFloat | None = None
        self.__prompt_float = PromptFloat()
        self.__content: list[Float] = []

    @property
    def float(self) -> BaseFloat | None:
        return self.__float

    @float.setter
    def float(self, value: BaseFloat | None) -> None:
        self.__float = value
        self.__update_float_containers()

    @property
    def error_float(self) -> ErrorFloat | None:
        return self.__error_float

    @error_float.setter
    def error_float(self, value: ErrorFloat | None) -> None:
        self.__error_float = value
        self.__update_float_containers()

    @property
    def prompt_float(self) -> PromptFloat:
        return self.__prompt_float

    @property
    def content(self) -> list[Float]:
        return self.__content

    def toggle_prompt(self) -> None:
        if self.__prompt_float.container in self.__content:
            self.__content.remove(self.__prompt_float.container)
            set_focus(get_view_manager().active_container)
        else:
            self.__content.append(self.__prompt_float.container)
            set_focus(self.__prompt_float.container.content)

    def __update_float_containers(self) -> None:
        result: list[Float] = []

        if self.float is not None:
            result.append(self.float.container)
            set_focus(self.float.container.content)

        if self.error_float is not None:
            result.append(self.error_float.container)
            set_focus(self.error_float.container.content)

        self.__content = result
        self._parent.rebuild()
