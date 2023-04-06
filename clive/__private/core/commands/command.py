from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from clive.__private.abstract_class import AbstractClass

T = TypeVar("T")


class Command(Generic[T], AbstractClass):
    """Command is an abstract class that defines a common interface for executing commands. The execute() method should
    be overridden by subclasses to implement the specific functionality of the command. The result property can be used
    to set and access the result of the command, which is initially set to None. Subclasses should set the result
    property with the output, if any.

    Args:
        result_default: The default (initial) value for the result property.
    """

    def __init__(self, *, result_default: T | None = None) -> None:
        self._result = result_default

    @property
    def result(self) -> T:
        """Get the result of the command.
        Returns:
            The result of the command.

        Raises:
            ValueError: If the result has not been set before.
        """
        if self._result is None:
            raise ValueError("The result is not set yet.")
        return self._result

    @result.setter
    def result(self, value: T) -> None:
        self._result = value

    @abstractmethod
    def execute(self) -> None:
        """Executes the command. The result could be set and accessed via the `result` property."""
