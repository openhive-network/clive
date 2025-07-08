from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal

from clive.__private.core.commands.abc.command_with_result import CommandResultT, CommandWithResult
from clive.__private.core.error_handlers.abc.error_handler_context_manager import ResultNotAvailable
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.commands.abc.command import Command


@dataclass(kw_only=True)
class ErrorHolder:
    error: BaseException | None = None

    @property
    def error_occurred(self) -> bool:
        return self.error is not None

    @property
    def success(self) -> bool:
        return not self.error_occurred

    def raise_if_error_occurred(self) -> None:
        if self.error_occurred:
            assert self.error is not None
            raise self.error


@dataclass(kw_only=True)
class CommandWrapper(ErrorHolder):
    command: Command


@dataclass(kw_only=True)
class NoOpWrapper(ErrorHolder):
    error: Literal[None] = None


class ResultNotAvailableError(CliveError):
    """Raised when a command's result is not available."""


@dataclass(kw_only=True)
class CommandWithResultWrapper(Generic[CommandResultT], ErrorHolder):
    command: CommandWithResult[CommandResultT]
    result: CommandResultT | ResultNotAvailable

    @property
    def result_or_raise(self) -> CommandResultT:
        """
        Returns the result of the command if it was successful, otherwise raises an exception.

        Raises:
            ResultNotAvailableError: if the command failed.
        """
        if isinstance(self.result, ResultNotAvailable):
            raise ResultNotAvailableError(f"Result is not available because the command failed with error={self.error}")
        return self.result
