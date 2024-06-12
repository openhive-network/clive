from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_active import CommandInActive, CommandRequiresActiveModeError
from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError
from clive.__private.core.error_handlers.failed_command_notificator import FailedCommandNotificator


@dataclass(kw_only=True)
class MockCommand(Command):
    async def _execute(self) -> None:
        """Just a mock command."""


@dataclass(kw_only=True)
class MockCommandInActive(CommandInActive):
    app_state: None = field(init=False, default=None)  # type: ignore[assignment]

    async def _execute(self) -> None:
        """Just a mock command."""

    async def _is_execution_possible(self) -> bool:
        return True


@pytest.mark.parametrize("exception", [CommandError, CommandExecutionNotPossibleError, CommandRequiresActiveModeError])
async def test_catching_correct_exception(exception: type[CommandError]) -> None:
    async with FailedCommandNotificator():
        raise exception(MockCommand())


@pytest.mark.parametrize("exception", [Exception, AssertionError, ValueError, TypeError])
async def test_catching_incorrect_exception(exception: type[Exception]) -> None:
    with pytest.raises(exception):
        async with FailedCommandNotificator():
            raise exception


async def test_catch_only() -> None:
    async with FailedCommandNotificator(catch_only=CommandRequiresActiveModeError):
        raise CommandRequiresActiveModeError(MockCommandInActive())

    with pytest.raises(CommandError):
        async with FailedCommandNotificator(catch_only=CommandRequiresActiveModeError):
            raise CommandError(MockCommand())
