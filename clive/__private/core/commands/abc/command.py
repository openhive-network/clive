from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from clive.__private.logger import logger


@dataclass(kw_only=True)
class Command(ABC):
    """
    Command is an abstract class that defines a common interface for executing commands. The execute() method should
    be overridden by subclasses to implement the specific functionality of the command.
    """

    @abstractmethod
    def _execute(self) -> None:
        """
        Proxy method for the execute() method. This method should be overridden by subclasses to implement the specific
        functionality of the command. The result could be set via the `result` property.
        """

    def execute(self) -> None:
        """Executes the command. The result could be accessed via the `result` property."""
        self._log_execution_info()
        self._execute()

    @staticmethod
    def execute_multiple(*commands: Command) -> None:
        for command in commands:
            command.execute()

    def _log_execution_info(self) -> None:
        logger.info(f"Executing command: {self.__class__.__name__}")
