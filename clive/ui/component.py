from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from prompt_toolkit.layout import AnyContainer

from clive.ui.parented import Parented
from clive.ui.rebuildable import Rebuildable

T = TypeVar("T", bound=Rebuildable)


class Component(Parented[T], Rebuildable, ABC):
    """A component is a part of an application that can be displayed on the screen in another component or view."""

    def __init__(self, parent: T) -> None:
        super().__init__(parent)
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
        """Create a container containing all the elements that define the layout."""

    def _rebuild(self, self_only: bool = False) -> None:
        """Rebuilds the current component and then calls the _rebuild method of its parent to propagate the change."""
        self._container = self._create_container()
        if not self_only:
            self._parent._rebuild()
