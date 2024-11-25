from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked, CommandRequiresUnlockedModeError
from clive.__private.core.commands.abc.command_restricted import CommandExecutionNotPossibleError
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.core.error_handlers.failed_command_notificator import FailedCommandNotificator


@dataclass(kw_only=True)
class MockCommand(Command):
    async def _execute(self) -> None:
        """Just a mock command."""


@dataclass(kw_only=True)
class MockCommandInUnlocked(CommandInUnlocked):
    wallet: None = field(init=False, default=None)  # type: ignore[assignment]

    async def _execute(self) -> None:
        """Just a mock command."""

    async def _is_execution_possible(self) -> bool:
        return True


@pytest.mark.parametrize(
    "exception", [CommandError, CommandExecutionNotPossibleError, CommandRequiresUnlockedModeError]
)
async def test_catching_correct_exception(exception: type[CommandError]) -> None:
    # ACT & ASSERT
    with pytest.raises(CannotNotifyError) as error_info:
        async with FailedCommandNotificator():
            raise exception(MockCommand())

    assert isinstance(error_info.value.error, exception), "The caught exception is not the expected one."


@pytest.mark.parametrize("exception", [Exception, AssertionError, ValueError, TypeError])
async def test_catching_incorrect_exception(exception: type[Exception]) -> None:
    # ACT & ASSERT
    with pytest.raises(exception):
        async with FailedCommandNotificator():
            raise exception


async def test_catch_only() -> None:
    # ARRANGE
    catch_only = CommandRequiresUnlockedModeError

    # ACT & ASSERT
    with pytest.raises(CannotNotifyError) as error_info:
        async with FailedCommandNotificator(catch_only=catch_only):
            raise catch_only(MockCommandInUnlocked())

    assert isinstance(error_info.value.error, catch_only), "The caught exception is not the expected one."

    with pytest.raises(CommandError):
        async with FailedCommandNotificator(catch_only=catch_only):
            raise CommandError(MockCommand())
