from __future__ import annotations

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.view import View


class ConvertView(View):
    def __init__(self, source_asset: str, destination_asset: str) -> None:
        self.__source_asset = source_asset
        self.__dest_asset = destination_asset
        super().__init__()

    def _create_container(self) -> AnyContainer:
        return Label(text=self.__class__.__name__)
