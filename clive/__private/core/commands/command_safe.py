from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar, ClassVar

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.command import Command
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import CliveError

CommandT = TypeVar("CommandT")

ExecutionNotPossibleCallbackT = Callable[[], None]
ExecutionNotPossibleCallbackOptionalT = ExecutionNotPossibleCallbackT | None


class CommandSafeExecutionError(CliveError):
    """Raised when (CommandSafe) safe command execution fails due to some reason."""


@dataclass(kw_only=True)
class CommandSafe(Command[CommandT], ABC):
    """
    A command that requires some conditions to be met before it can be executed.
    """

    skip_execution_not_possible_callback: bool = False
    execution_not_possible_callback: ExecutionNotPossibleCallbackOptionalT = None
    _exception: ClassVar[CliveError] = CommandSafeExecutionError()

    def execute_safely(self) -> None:
        """
        Raises:
            CommandExecutionFailed: if the execution of the command has failed when executed via `execute_safely`.

        Example usage:

        try:
            some_command.execute_safely()
        except CommandSafeExecutionError:
            # handle situation when command execution has failed
        else:
            # handle situation when command execution succeeded
        """
        if not self._is_execution_possible():
            self._before_execution_not_possible_callback()
            if callback := self.execution_not_possible_callback:
                callback()
            self._after_execution_not_possible_callback()
            raise self._exception

        self.execute()

    def _is_execution_possible(self) -> bool:
        return True

    def _before_execution_not_possible_callback(self) -> None:
        """
        Called when the execution of the command is not possible, before calling the execution_not_possible_callback.
        """
        if self.skip_execution_not_possible_callback:
            raise RuntimeError(
                "Execution of the command is not possible, but the execution_not_possible_callback has been skipped."
            )

    def _after_execution_not_possible_callback(self) -> None:
        """
        Called when the execution of the command is not possible, after calling the execution_not_possible_callback.
        """
        self._notify()

    def _notify(self) -> None:
        if get_clive().is_launched:
            self._notify_tui()

    def _notify_tui(self) -> None:
        Notification("Action failed. Please try again...", category="error").show()
