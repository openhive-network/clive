from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from clive.__private.abstract_class import AbstractClass

T = TypeVar("T")


@dataclass
class Command(Generic[T], AbstractClass):
    """Command is an abstract class that defines a common interface for executing commands. The execute() method should
    be overridden by subclasses to implement the specific functionality of the command. The result property can be used
    to set and access the result of the command, which is initially set to None. Subclasses should set the result
    property with the output, if any.

    Args:
        result_default: The default (initial) value for the result property.
    """

    @property
    def result(self) -> T:
        """Get the result of the command.
        Returns:
            The result of the command.

        Raises:
            ValueError: If the result has not been set before.
        """
        self._result: T | None
        if not hasattr(self, "_result") or self._result is None:
            raise ValueError("The result is not set yet.")
        return self._result

    @abstractmethod
    def execute(self) -> None:
        """Executes the command. The result could be set and accessed via the `result` property."""

    @classmethod
    def execute_with_result(cls, command: Command[T]) -> T:
        command.execute()
        return command.result
