from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from clive.__private.abstract_class import AbstractClass

T = TypeVar("T")


class Command(Generic[T], AbstractClass):
    def __init__(self) -> None:
        self._result: T | None = None

    @property
    def result(self) -> T:
        if self._result is None:
            raise ValueError("The result is not set yet.")
        return self._result

    @result.setter
    def result(self, value: T) -> None:
        self._result = value

    @abstractmethod
    def execute(self) -> None:
        """Executes the command. The result could be set and accessed via the `result` property."""
