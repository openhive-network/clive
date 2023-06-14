from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.command import Command, CommandT
from clive.__private.ui.activate.activate import ActivationResultCallbackT
from test_tools import logger

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState

ActivateCallbackT = Callable[[ActivationResultCallbackT], bool]
ActivateCallbackOptionalT = ActivateCallbackT | None


@dataclass(kw_only=True)
class CommandInActive(Command[CommandT], ABC):
    """
    CommandInActive is an abstract class that defines a common interface for executing commands that require the
    application to be in active mode. If the application is not in active mode, the command will try to activate
    and then execute the command.
    """

    app_state: AppState
    skip_activate: bool = False
    activate_callback: ClassVar[ActivateCallbackOptionalT] = None

    def __post_init__(self):
        self._result_set_event = asyncio.Event()

    @classmethod
    def register_activate_callback(cls, callback: ActivateCallbackOptionalT) -> None:
        cls.activate_callback = callback

    def execute(self) -> None:
        if not self.app_state.is_active():
            if self.skip_activate:
                raise AssertionError("The application is not in active mode when skip_activate is set.")
            assert self.activate_callback, "The activate callback should be set."
            self.activate_callback(self.__check_result)
        else:
            super().execute()

    def __check_result(self, result: bool) -> None:
        if result:
            super().execute()
        else:
            self.execute()  # try to activate again

    async def execute_with_result(self) -> CommandT:
        self.execute()
        logger.debug(f"Waiting for result of command: {self.__class__.__name__}")
        await self._result_set_event.wait()
        logger.debug(f"Result of command: {self.__class__.__name__} is set to {self.result}.")
        return self.result
