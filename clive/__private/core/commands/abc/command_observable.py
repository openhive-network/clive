from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import blinker

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_with_result import CommandResultT
from clive.__private.logger import logger
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from typing_extensions import Self

SenderT = TypeVar("SenderT", bound="CommandObservable[Any]")
ResultCallbackT = Callable[[SenderT, CommandResultT | None, Exception | None], None]


class CommandInterruptedError(CliveError):
    def __init__(self, command: Command) -> None:
        super().__init__(f"Command {command.__class__.__name__} has been interrupted.")


@dataclass(kw_only=True)
class CommandObservable(Command, Generic[CommandResultT], ABC):
    _is_armed: bool = field(init=False, default=False)
    _is_interrupted: bool = field(init=False, default=False)

    _wait_for_me: bool = field(init=False, default=False)  # TODO

    _result: CommandResultT | None = field(init=False, default=None)

    executed: blinker.Signal = field(default_factory=lambda: blinker.Signal())
    _finished: blinker.Signal = field(init=False, default_factory=lambda: blinker.Signal())  # TODO

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def _arm(self, **kwargs: Any) -> None:
        """All members required before the command execution should be set via this method."""

    def arm(self, **kwargs: Any) -> None:
        self._arm(**kwargs)
        self._is_armed = True

    def fire(self) -> None:
        assert self._is_armed, "Command must be armed before it can be fired!"
        assert not self._is_interrupted, "Cannot fire a command after it has been interrupted!"
        self._log_execution_info()

        if self._finished.receivers:
            self._execute()
            return

        try:
            self._execute()
        except Exception as error:  # noqa: BLE001
            logger.debug(f"{self.__class__.__name__}._execute() failed. Notifying with {error=}")
            self.executed.send(self, result=None, exception=error)
        else:
            logger.debug(f"{self.__class__.__name__}._execute() succeeded. Notifying with {self._result=}")
            self.executed.send(self, result=self._result, exception=None)

    def _set_finish_on_finished_signal(self) -> None:
        def __on_finished_result(
            _: SenderT, result: CommandResultT | None, exception: Exception | None
        ) -> None:  # TODO
            logger.debug(
                f"{self.__class__.__name__}._execute() succeeded via finished_signal. Notifying with {self._result=}"
            )

            data = (
                {"result": None, "exception": exception}
                if exception
                else {"result": result or self._result, "exception": None}
            )
            self.executed.send(self, **data)

        self._finished.connect(__on_finished_result, weak=False)

    def interrupt(self, *, with_result: CommandResultT | None = None) -> None:
        logger.debug(f"Command {self.__class__.__name__} has been interrupted.")
        self._is_interrupted = True
        result = with_result or self._result
        self.executed.send(self, result=result, exception=CommandInterruptedError(self))

    def observe_result(self, callback: ResultCallbackT[Self, CommandResultT]) -> None:
        self.executed.connect(callback, weak=False)
