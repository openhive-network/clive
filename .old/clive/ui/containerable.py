from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer, Float

T = TypeVar("T", bound="AnyContainer | Float")


class Containerable(Generic[T], ABC):
    """
    An abstract base class for classes that have a container.
    This class is used for holding a `_container` member, which is an instance of `AnyContainer`
    from `prompt_toolkit` library.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._container = self._create_container()

        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

    @abstractmethod
    def _create_container(self) -> T:
        """Create a container containing all the elements that define the layout."""

    @property
    def container(self) -> T:
        return self._container
