from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.component import Component

class ExitConfirmationView(Component):
    def _create_container(self) -> AnyContainer:
        exit(0)
        return Label(text=self.__class__.__name__)

