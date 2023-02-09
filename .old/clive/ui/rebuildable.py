from __future__ import annotations

from abc import ABC, abstractmethod


class Rebuildable(ABC):
    """An abstract class for objects that can be rebuilt."""

    @abstractmethod
    def _rebuild(self) -> None:
        """Should rebuild the object which means that e.g. it updates references or creates some elements again."""
