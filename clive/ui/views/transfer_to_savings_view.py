from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.view import View


class TransferToSavingsView(View):
    def __init__(self, asset: str) -> None:
        self.__asset = asset
        super().__init__()

    def _create_container(self) -> AnyContainer:
        return Label(text=self.__class__.__name__)
