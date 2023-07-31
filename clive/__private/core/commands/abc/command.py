from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from clive.__private.logger import logger
from clive.exceptions import CliveError


class CommandError(CliveError):
    def __init__(self, command: Command, message: str = "") -> None:
        self.command = command
        self.message = f"Command {command.__class__.__name__} failed. Reason: {message}"
        super().__init__(self.message)


class SynchronousOnlyCommandError(CommandError):
    """Raised by commands, that are dedicated to be executed only via execute."""


class AsynchronousOnlyCommandError(CommandError):
    """Raised by commands, that are dedicated to be executed only via async_execute."""


@dataclass(kw_only=True)
class Command(ABC):  # noqa: B024
    """An abstract class that defines a common interface for executing commands."""

    def _execute(self) -> None:
        """
        Proxy method for the execute() method.

        The result could be set via the `result` property.
        """
        raise AsynchronousOnlyCommandError(self)

    def execute(self) -> None:
        """Executes the command. The result could be accessed via the `result` property."""
        self._log_execution_info()
        self._execute()

    async def _async_execute(self) -> None:
        """
        Proxy method for the async_execute() method.

        The result could be set via the `result` property.
        """
        raise SynchronousOnlyCommandError(self)

    async def async_execute(self) -> None:
        """Executes the command. The result could be accessed via the `result` property."""
        self._log_execution_info()
        await self._async_execute()

    @staticmethod
    def execute_multiple(*commands: Command) -> None:
        for command in commands:
            command.execute()

    def _log_execution_info(self) -> None:
        logger.info(f"Executing command: {self.__class__.__name__}")
