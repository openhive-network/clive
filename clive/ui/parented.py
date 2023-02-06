from __future__ import annotations

from abc import ABC
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Parented(Generic[T], ABC):
    """An abstract class for objects that have a parent."""

    def __init__(self, parent: T, *args: Any, **kwargs: Any) -> None:
        self._parent = parent

        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)
