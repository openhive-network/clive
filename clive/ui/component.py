from __future__ import annotations

from abc import ABC, abstractmethod

from loguru import logger
from prompt_toolkit.layout import AnyContainer


class Component(ABC):
    """
    A component is a part of an application that can be displayed on the screen in another component
    or as a separate view.
    """

    def __init__(self) -> None:
        self._registered_components: list[Component] = []
        self._container = self._create_container()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return str(self)

    @property
    def container(self) -> AnyContainer:
        return self._container

    @abstractmethod
    def _create_container(self) -> AnyContainer:
        """Create the container holding all the component's elements defining its layout."""

    def register_component(self, component: Component) -> Component:
        self._registered_components.append(component)
        return component

    def rebuild(self) -> None:
        self._container = self._create_container()

    def register_decorator(func):
        def wrapper(self, *args, **kwargs):
            component = args[0]
            logger.warning("COMP", args, kwargs)
            self._registered_components.remove(component)
            func(*args)
            self.register_component(component)
            return component

        return wrapper
