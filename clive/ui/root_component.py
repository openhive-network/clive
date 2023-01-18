from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.widgets import Label

from clive.ui.dynamic_component import DynamicComponent

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer

    from clive.ui.component import Component


class RootComponent(DynamicComponent):
    """A root component that contains all other components. Should be created only once."""

    def __init__(self) -> None:
        self.__component: Component | None = None
        self.__default_container = Label(text="No view selected... Loading...")
        super().__init__()

    def _create_container(self) -> AnyContainer:
        return self.__component.container if self.__component else self.__default_container

    @property
    def component(self) -> Component | None:
        return self.__component

    @component.setter
    def component(self, component: Component) -> None:
        self.__component = component


root_component = RootComponent()
