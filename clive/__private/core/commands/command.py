from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from clive.__private.abstract_class import AbstractClass
from clive.__private.core.clive_import import get_clive
from clive.__private.logger import logger
from clive.__private.ui.widgets.notification import Notification

CommandT = TypeVar("CommandT")

ExecutionNotPossibleCallbackT = Callable[[], None]
ExecutionNotPossibleCallbackOptionalT = ExecutionNotPossibleCallbackT | None


@dataclass(kw_only=True)
class Command(Generic[CommandT], AbstractClass):
    """Command is an abstract class that defines a common interface for executing commands. The execute() method should
    be overridden by subclasses to implement the specific functionality of the command. The result property can be used
    to set and access the result of the command, which is initially set to None. Subclasses should set the result
    property with the output, if any.
    """

    _result: CommandT | None = field(default=None, init=False)
    execution_not_possible_callback: ExecutionNotPossibleCallbackOptionalT = None

    @property
    def result(self) -> CommandT:
        """Get the result of the command.
        Returns:
            The result of the command.

        Raises:
            ValueError: If the result has not been set before.
        """
        if self._result is None:
            logger.error(f"{self.__class__.__name__} command result has not been set when accessed!")
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
        logger.info(f"Executing command: {self.__class__.__name__}")
        self._execute()

    def execute_with_result(self) -> CommandT:
        self.execute()
        return self.result

    @staticmethod
    def execute_multiple(*commands: Command[Any]) -> None:
        for command in commands:
            command.execute()

    def execute_safely(self) -> bool:
        if not self._is_execution_possible():
            if callback := self.execution_not_possible_callback:
                callback()
            self._on_execution_failed()
            return False

        self.execute()
        return True

    def _is_execution_possible(self) -> bool:
        return True

    def _on_execution_failed(self) -> None:
        """Called when the execution of the command has failed, after calling the execution_not_possible_callback."""
        self._notify()

    def _notify(self) -> None:
        if get_clive().is_launched:
            self._notify_tui()

    def _notify_tui(self) -> None:
        Notification("Action failed. Please try again...", category="error").show()
