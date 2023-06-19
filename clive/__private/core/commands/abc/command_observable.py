from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import blinker

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_with_result import CommandResultT
from clive.__private.logger import logger

if TYPE_CHECKING:
    from typing_extensions import Self

SenderT = TypeVar("SenderT", bound="CommandObservable[Any]")
ResultCallbackT = Callable[[SenderT, CommandResultT | None, Exception | None], None]


@dataclass(kw_only=True)
class CommandObservable(Command, Generic[CommandResultT], ABC):
    _is_armed: bool = False
    _result: CommandResultT | None = field(init=False, default=None)

    executed: blinker.Signal = field(default_factory=lambda: blinker.Signal())

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def _arm(self, **kwargs: Any) -> None:
        """All members required before the command execution should be set via this method."""

    def arm(self, **kwargs: Any) -> None:
        self._arm(**kwargs)
        self._is_armed = True

    def fire(self) -> None:
        assert self._is_armed, "Command must be armed before it can be fired!"
        self._log_execution_info()

        try:
            self._execute()
        except Exception as error:  # noqa: BLE001
            logger.debug(f"{self.__class__.__name__}._execute() failed. Notifying with {error=}")
            self.executed.send(self, result=None, exception=error)
        else:
            logger.debug(f"{self.__class__.__name__}._execute() succeeded. Notifying with {self._result=}")
            self.executed.send(self, result=self._result, exception=None)

    def observe_result(self, callback: ResultCallbackT[Self, CommandResultT]) -> None:
        self.executed.connect(callback, weak=False)
