from __future__ import annotations

from typing import Any, Generic, TypeVar

from clive.abstract_class import AbstractClass

T = TypeVar("T")


class Parented(Generic[T], AbstractClass):
    """An abstract class for objects that have a parent."""

    def __init__(self, parent: T, *args: Any, **kwargs: Any) -> None:
        self._parent = parent

        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)
