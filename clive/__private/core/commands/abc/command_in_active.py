from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_observable import CommandObservable, SenderT
from clive.__private.core.commands.abc.command_with_result import CommandResultT
from clive.__private.core.commands.activate_extended import ActivateExtended
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState


ActivationCallbackT = Callable[["CommandObservable"], None]
ActivationCallbackOptionalT = ActivationCallbackT | None


@dataclass(kw_only=True)
class CommandInActive(CommandObservable[CommandResultT], ABC):
    """
    A command that require the application to be in active mode. If the application is not in active mode, the command
    will try to activate and then command can be executed.
    """

    app_state: AppState
    skip_activate: bool = False

    def execute(self) -> None:
        command = ActivateExtended(app_state=self.app_state, skip_activate=self.skip_activate)
        command.observe_result(self.__on_activation_result)
        command.execute()

    def __on_activation_result(
        self, _: SenderT, result: bool | None, exception: Exception | None  # noqa: ARG002
    ) -> None:
        logger.debug(f"Command {self.__class__.__name__} activation result: {result}")

        if result:
            self.fire()
