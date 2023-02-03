from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, TypeVar

from loguru import logger

from clive.ui.containerable import Containerable
from clive.ui.parented import Parented
from clive.ui.rebuildable import Rebuildable

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer  # noqa: F401

T = TypeVar("T", bound=Rebuildable)


class Component(Parented[T], Containerable["AnyContainer"], Rebuildable, ABC):
    """A component is a part of an application that can be displayed on the screen in another component or view."""

    def __init__(self, parent: T) -> None:
        super().__init__(parent)
        self._container = self._create_container()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return str(self)

    def _rebuild(self) -> None:
        """Rebuilds the current component and then calls the _rebuild method of its parent to propagate the change."""
        logger.debug(f"rebuilding component: {self.__class__.__name__}")
        self._container = self._create_container()
        self._parent._rebuild()
