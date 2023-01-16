from __future__ import annotations

from abc import ABC

from prompt_toolkit.layout import AnyContainer

from clive.ui.component import Component


class DynamicComponent(Component, ABC):
    """A component that allows for changing its container entirely at runtime."""

    @property
    def container(self) -> AnyContainer:
        """Get the container holding all the component's elements"""
        return self._container

    @container.setter
    def container(self, container: AnyContainer) -> None:
        self._container = container
