from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

from clive.__private.logger import logger
from clive.exceptions import CliveError


class CommandError(CliveError):
    def __init__(self, command: Command, reason: str = "") -> None:
        self.command = command
        self.reason = reason
        message = f"Command {command.__class__.__name__} failed. Reason: {reason}"
        super().__init__(message)


@dataclass(kw_only=True)
class Command(ABC):
    """An abstract class that defines a common interface for executing commands."""

    @property
    def _should_skip_execution(self) -> bool:
        return False

    @abstractmethod
    async def _execute(self) -> None:
        """
        Proxy method for the execute() method.

        The result could be set via the `result` property.
        """

    async def execute(self) -> None:
        """Execute the command. The result could be accessed via the `result` property."""
        if self._should_skip_execution:
            self._log_execution_skipped()
            return
        self._log_execution_info()
        await self._execute()

    @staticmethod
    async def execute_multiple(*commands: Command) -> None:
        asyncio.gather(*[command.execute() for command in commands])

    def _log_execution_info(self) -> None:
        logger.debug(f"Executing command: {self.__class__.__name__}")

    def _log_execution_skipped(self) -> None:
        logger.debug(f"Skipping execution of command: {self.__class__.__name__}")
