from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.component import Component
from clive.ui.rebuildable import Rebuildable

class AccountHistoryView(Component[Rebuildable]):

    def __init__(self, parent: Rebuildable) -> None:
        super().__init__(parent)

    def _create_container(self) -> AnyContainer:
        return Label(text=self.__class__.__name__)
