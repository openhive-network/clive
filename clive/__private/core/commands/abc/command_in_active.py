from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Protocol

from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError, CommandRestricted


class AppStateProtocol(Protocol):
    @property
    def is_active(self) -> bool:
        ...


class CommandRequiresActiveModeError(CommandExecutionNotPossibleError):
    def __init__(self, command: CommandInActive) -> None:
        super().__init__(command, message="requires the application to be in active mode.")


@dataclass(kw_only=True)
class CommandInActive(CommandRestricted, ABC):
    """A command that require the application to be in active mode."""

    app_state: AppStateProtocol

    _execution_impossible_error: ClassVar[type[CommandExecutionNotPossibleError]] = CommandRequiresActiveModeError

    def _is_execution_possible(self) -> bool:
        return self.app_state.is_active
