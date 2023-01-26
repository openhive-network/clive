from abc import ABC

from clive.ui.containerable import Containerable
from clive.ui.focus import set_focus
from clive.ui.get_view_manager import get_view_manager


class BaseFloat(Containerable, ABC):
    """
    By deriving from this class you can create float which
    will be automatically visible after creation
    """

    def __init__(self) -> None:
        super().__init__()
        get_view_manager().menu.float = self
        set_focus(self.container)

    def _close(self) -> None:
        get_view_manager().menu.float = None
