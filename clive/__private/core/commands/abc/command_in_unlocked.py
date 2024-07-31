from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Protocol

from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError, CommandRestricted


class AppStateProtocol(Protocol):
    @property
    def is_unlocked(self) -> bool: ...


class CommandRequiresUnlockedModeError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandInUnlocked) -> None:
        super().__init__(command, reason="requires the application to be in unlocked mode.")


@dataclass(kw_only=True)
class CommandInUnlocked(CommandRestricted, ABC):
    """A command that require the application to be in unlocked mode."""

    app_state: AppStateProtocol

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandRequiresUnlockedModeError

    async def _is_execution_possible(self) -> bool:
        return self.app_state.is_unlocked
