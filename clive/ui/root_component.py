from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import VSplit, WindowAlign
from prompt_toolkit.widgets import Label

from clive.ui.component import Component

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class RootComponent(Component):
    """A root component that contains all other components. Should be created only once."""

    def __init__(self) -> None:
        super().__init__()
        self.__root_container = self._container

    def _create_container(self) -> VSplit:
        return VSplit(
            [
                Label(text="No view selected", align=WindowAlign.CENTER),
            ]
        )

    @property
    def container(self) -> AnyContainer:
        return self.__root_container

    @container.setter
    def container(self, value: AnyContainer) -> None:
        self.__root_container.children = [value]


root_component = RootComponent()
