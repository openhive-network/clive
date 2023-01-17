from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from prompt_toolkit.layout import DynamicContainer
from prompt_toolkit.widgets import Label

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer

components_before = []


class RootComponent:
    """A root component that contains all other components. Should be created only once."""

    def __init__(self) -> None:
        self.__container: AnyContainer = Label(text="No view selected... Loading...")
        from clive.ui.welcome_component import WelcomeComponent

        self.component = WelcomeComponent()
        self.__root_container = self.__create_container()

    def __create_container(self) -> DynamicContainer:
        return DynamicContainer(
            lambda: self.__container if not self.component else self.component.container,
        )

    @property
    def container(self) -> AnyContainer:
        return self.__root_container

    @container.setter
    def container(self, value: AnyContainer) -> None:
        self.__container = value

    def invalidate(self) -> None:
        """Invalidate the root container and all its children."""
        from clive.app import clive

        components = list(self.iterate(self.component))

        if components_before and components_before != components:
            components_before.clear()
            components_before.extend(components)

            logger.debug(f"Invalidating {components} components")
            for component in components:
                component.rebuild()
            clive.set_focus(components[-1].container)

        elif not components_before:
            components_before.extend(components)

    # get all nodes recursively
    def iterate(self, node):
        for child in node._registered_components:
            yield from self.iterate(child)
        yield node


root_component = RootComponent()
