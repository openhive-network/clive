from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.command import Command, CommandT

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState

ActivateCallbackT = Callable[[], None] | None


@dataclass(kw_only=True)
class CommandInActive(Command[CommandT], ABC):
    """
    CommandInActive is an abstract class that defines a common interface for executing commands that require the
    application to be in active mode. If the application is not in active mode, the command will try to activate
    and then execute the command.
    """

    app_state: AppState
    skip_activate: bool = False
    activate_callback: ClassVar[ActivateCallbackT] = None

    @classmethod
    def register_activate_callback(cls, callback: ActivateCallbackT) -> None:
        cls.activate_callback = callback

    def execute(self) -> None:
        if not self.app_state.is_active():
            if self.skip_activate:
                raise AssertionError("The application is not in active mode.")
            assert self.activate_callback, "The activate callback should be set."
            self.activate_callback()
        self._execute()
