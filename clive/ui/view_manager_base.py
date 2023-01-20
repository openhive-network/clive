from abc import ABC
from prompt_toolkit.layout import VSplit, AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.rebuildable import Rebuildable

class ViewManagerBase(Rebuildable, ABC):
    def __init__(self) -> None:
        self._default_container = Label(text="No view selected... Loading...")
        self._root_container = VSplit([self._default_container])

    @property
    def active_container(self) -> AnyContainer:
        return self._root_container

