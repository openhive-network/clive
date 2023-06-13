from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from clive.__private.abstract_class import AbstractClass

CommandT = TypeVar("CommandT")


@dataclass
class Command(Generic[CommandT], AbstractClass):
    """Command is an abstract class that defines a common interface for executing commands. The execute() method should
    be overridden by subclasses to implement the specific functionality of the command. The result property can be used
    to set and access the result of the command, which is initially set to None. Subclasses should set the result
    property with the output, if any.
    """

    _result: CommandT | None = field(default=None, init=False)

    @property
    def result(self) -> CommandT:
        """Get the result of the command.
        Returns:
            The result of the command.

        Raises:
            ValueError: If the result has not been set before.
        """
        if self._result is None:
            raise ValueError("The result is not set yet.")
        return self._result

    @abstractmethod
    def _execute(self) -> None:
        """
        Proxy method for the execute() method. This method should be overridden by subclasses to implement the specific
        functionality of the command. The result could be set via the `result` property.
        """

    def execute(self) -> None:
        """Executes the command. The result could be accessed via the `result` property."""
        self._execute()

    def execute_with_result(self) -> CommandT:
        self.execute()
        return self.result
