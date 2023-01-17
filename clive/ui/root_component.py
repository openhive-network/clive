from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import DynamicContainer
from prompt_toolkit.widgets import Label

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class RootComponent:
    """A root component that contains all other components. Should be created only once."""

    def __init__(self) -> None:
        self.__container: AnyContainer = Label(text="No view selected... Loading...")
        self.__root_container = self.__create_container()

    def __create_container(self) -> DynamicContainer:
        return DynamicContainer(
            lambda: self.__container,
        )

    @property
    def container(self) -> AnyContainer:
        return self.__root_container

    @container.setter
    def container(self, value: AnyContainer) -> None:
        self.__container = value


root_component = RootComponent()
