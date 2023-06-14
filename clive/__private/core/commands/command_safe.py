from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from clive.__private.core.clive_import import get_clive
from clive.__private.core.commands.command import Command
from clive.__private.ui.widgets.notification import Notification

CommandT = TypeVar("CommandT")

ExecutionNotPossibleCallbackT = Callable[[], None]
ExecutionNotPossibleCallbackOptionalT = ExecutionNotPossibleCallbackT | None


@dataclass(kw_only=True)
class CommandSafe(Command[CommandT], ABC):
    """
    A command that requires some conditions to be met before it can be executed.
    """

    execution_not_possible_callback: ExecutionNotPossibleCallbackOptionalT = None

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
