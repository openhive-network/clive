from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command, CommandT

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class CommandInActive(Command[CommandT], ABC):
    """
    CommandInActive is an abstract class that defines a common interface for executing commands that require the
    application to be in active mode. If the application is not in active mode, the command will try to activate
    and then execute the command.
    """

    app_state: AppState
    activate_callback: Callable[[], None] | None = None
    skip_activate: bool = False

    def __post_init__(self) -> None:
        if not self.skip_activate and not self.activate_callback:
            raise ValueError(f"Either `{self.skip_activate=}` or `{self.activate_callback=}` must be set.")

    def execute(self) -> None:
        if not self.app_state.is_active():
            if self.skip_activate:
                raise AssertionError("The application is not in active mode.")
            assert self.activate_callback, "The activate callback should be set."
            self.activate_callback()
        self._execute()
