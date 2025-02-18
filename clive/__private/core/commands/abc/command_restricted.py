from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Final

from clive.__private.core.commands.abc.command import Command, CommandError


class CommandExecutionNotPossibleError(CommandError):
    _DEFAULT_REASON: Final[str] = "does not met the requirements to be executed."

    def __init__(self, command: CommandRestricted, *, reason: str = _DEFAULT_REASON) -> None:
        super().__init__(command, reason)


class CommandRestricted(Command, ABC):
    """A command that is conditioned before it can be executed."""

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandExecutionNotPossibleError

    async def execute(self) -> None:
        """
        Execute the command if the conditions are met.

        Raises
        ------
            CommandExecutionNotPossibleError: If the command cannot be executed.
        """
        if self._should_skip_execution:
            # _is_execution_possible should not be called if the execution is skipped
            await super().execute()
            return

        if not await self._is_execution_possible():
            raise self._execution_impossible_error(self)
        await super().execute()

    @abstractmethod
    async def _is_execution_possible(self) -> bool:
        """Condition that must be met for the command to be executed. If execution is not possible, error is raised."""
