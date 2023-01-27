from abc import ABC
from typing import Callable

from clive.ui.containerable import Containerable
from clive.ui.focus import set_focus
from clive.ui.get_view_manager import get_view_manager


class BaseFloat(Containerable, ABC):
    """
    By deriving from this class you can create float which
    will be automatically visible after creation
    """

    def __init__(self) -> None:
        self.__close_callback: Callable[[], None] = lambda: None
        super().__init__()
        get_view_manager().float = self
        set_focus(self.container)

    def _close(self) -> None:
        get_view_manager().float = None
        self.close_callback()

    @property
    def close_callback(self) -> Callable[[], None]:
        return self.__close_callback

    @close_callback.setter
    def close_callback(self, value: Callable[[], None]) -> None:
        self.__close_callback = value
