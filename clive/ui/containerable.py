from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class Containerable(ABC):
    """
    An abstract base class for classes that have a container.
    This class is used for holding a `_container` member, which is an instance of `AnyContainer`
    from `prompt_toolkit` library.
    """

    def __init__(self) -> None:
        self._container = self._create_container()

    @abstractmethod
    def _create_container(self) -> AnyContainer:
        """Create a container containing all the elements that define the layout."""

    @property
    def container(self) -> AnyContainer:
        return self._container
