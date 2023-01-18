from __future__ import annotations

from abc import ABC, abstractmethod

from prompt_toolkit.layout import AnyContainer, DynamicContainer


class Component(ABC):
    """
    A component is a part of an application that can be displayed on the screen in another component
    or as a separate view.
    """

    def __init__(self) -> None:
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


class DynamicComponent(Component, ABC):
    """A component that refreshes (rebuilds) its container automatically during runtime."""

    def __init__(self) -> None:
        super().__init__()
        self._container = DynamicContainer(lambda: self._create_container())
