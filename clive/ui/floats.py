from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import CompletionsMenu, Float

from clive.ui.focus import set_focus
from clive.ui.parented import Parented

if TYPE_CHECKING:
    from clive.ui.base_float import BaseFloat
    from clive.ui.catch import ErrorFloat
    from clive.ui.view_manager import ViewManager


class Floats(Parented["ViewManager"]):
    def __init__(self, parent: ViewManager) -> None:
        super().__init__(parent)

        self.__float: BaseFloat | None = None
        self.__error_float: ErrorFloat | None = None

        self.__completion_float = Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        )

        self.__content: list[Float] = [self.__completion_float]

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
    def completion_float(self) -> Float:
        return self.__completion_float

    @property
    def content(self) -> list[Float]:
        return self.__content

    def __update_float_containers(self) -> None:
        result: list[Float] = [self.__completion_float]

        if self.float is not None:
            result.append(self.float.container)
            set_focus(self.float.container.content)

        if self.error_float is not None:
            result.append(self.error_float.container)
            set_focus(self.error_float.container.content)

        self.__content = result
        self._parent.rebuild()
