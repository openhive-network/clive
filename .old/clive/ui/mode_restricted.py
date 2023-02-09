from __future__ import annotations

from typing import Any, Sequence

from clive.abstract_class import AbstractClass
from clive.app_status import app_status
from clive.enums import AppMode


class ModeRestricted(AbstractClass):
    def __init__(self, modes: Sequence[AppMode] = (AppMode.ANY,), *args: Any, **kwargs: Any) -> None:
        self.__modes = modes

        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

    def is_available(self) -> bool:
        current_mode = app_status.mode
        return AppMode.ANY in self.__modes or current_mode in self.__modes
