from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from clive.__private.core.commands.abc.command import Command
from clive.__private.logger import logger

CommandResultT = TypeVar("CommandResultT")


@dataclass(kw_only=True, replace=False)  # type: ignore[call-overload]
class CommandWithResult(Command, ABC, Generic[CommandResultT]):  # noqa: UP046
    """
    A command that returns a result.

    The result property can be used to set and access the result of the command,
    which is initially set to None. Subclasses should set the result property with the output, if any.
    """

    _result: CommandResultT | None = field(default=None, init=False)

    @property
    def result(self) -> CommandResultT:
        """
        Get the result of the command.

        Returns:
            The result of the command.

        Raises:
            ValueError: If the result has not been set before.
        """
        if self._result is None:
            logger.error(f"{self.__class__.__name__} command result has not been set when accessed!")
            raise ValueError("The result is not set yet.")
        return self._result

    async def execute_with_result(self) -> CommandResultT:
        await self.execute()
        return self.result
