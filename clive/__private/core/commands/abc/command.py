from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

from clive.__private.logger import logger
from clive.exceptions import CliveError


class CommandError(CliveError):
    def __init__(self, command: Command, message: str = "") -> None:
        self.command = command
        self.message = f"Command {command.__class__.__name__} failed. Reason: {message}"
        super().__init__(self.message)


@dataclass(kw_only=True)
class Command(ABC):
    """An abstract class that defines a common interface for executing commands."""

    @abstractmethod
    async def _execute(self) -> None:
        """
        Proxy method for the execute() method.

        The result could be set via the `result` property.
        """

    async def execute(self) -> None:
        """Executes the command. The result could be accessed via the `result` property."""
        self._log_execution_info()
        await self._execute()

    @staticmethod
    async def execute_multiple(*commands: Command) -> None:
        asyncio.gather(*[command.execute() for command in commands])

    def _log_execution_info(self) -> None:
        logger.info(f"Executing command: {self.__class__.__name__}")
