from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.command import (
    Command,
    CommandT,
    ExecutionNotPossibleCallbackOptionalT,
    ExecutionNotPossibleCallbackT,
)
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class CommandInActive(Command[CommandT], ABC):
    """
    CommandInActive is an abstract class that defines a common interface for executing commands that require the
    application to be in active mode. If the application is not in active mode, the command will try to activate
    and then command can be executed once again manually.
    """

    app_state: AppState
    skip_activate: bool = False
    activate_callback: ClassVar[ExecutionNotPossibleCallbackOptionalT] = None
    execution_not_possible_callback: ExecutionNotPossibleCallbackOptionalT = field(init=False)

    def __post_init__(self) -> None:
        self.execution_not_possible_callback = self.activate_callback

    @classmethod
    def register_activate_callback(cls, callback: ExecutionNotPossibleCallbackT) -> None:
        cls.activate_callback = callback

    def _is_execution_possible(self) -> bool:
        return self.app_state.is_active() or self.skip_activate

    def _notify_tui(self) -> None:
        Notification(
            "Active mode is required for this action! Please activate, and try again...", category="error"
        ).show()
