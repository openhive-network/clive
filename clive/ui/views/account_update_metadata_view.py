from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.component import Component

class AccountUpdateMetadataView(Component):
    def _create_container(self) -> AnyContainer:
        return Label(text=self.__class__.__name__)
