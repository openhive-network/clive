from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

T = TypeVar("T")


class Parented(Generic[T], ABC):
    """An abstract class for objects that have a parent."""

    def __init__(self, parent: T) -> None:
        self._parent = parent
