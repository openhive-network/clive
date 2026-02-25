from __future__ import annotations

from dataclasses import dataclass

import pytest

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.autosign import (
    AuthorityPrefetchAutoSignError,
    InsufficientKeysAutoSignError,
)
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator


@dataclass(kw_only=True)
class MockCommand(Command):
    async def _execute(self) -> None:
        """Just a mock command."""


@pytest.mark.parametrize(
    ("exception", "expected_message"),
    [
        (InsufficientKeysAutoSignError(MockCommand()), InsufficientKeysAutoSignError.REASON),
        (
            AuthorityPrefetchAutoSignError(MockCommand(), cause=RuntimeError("node error")),
            AuthorityPrefetchAutoSignError.REASON,
        ),
    ],
    ids=["InsufficientKeysAutoSignError", "AuthorityPrefetchAutoSignError"],
)
async def test_autosign_errors_are_caught(exception: Exception, expected_message: str) -> None:
    notificator = GeneralErrorNotificator()

    assert notificator._is_exception_to_catch(exception), f"{type(exception).__name__} should be caught"
    assert notificator._determine_message(exception) == expected_message


async def test_autosign_errors_raise_cannot_notify_when_tui_not_launched() -> None:
    with pytest.raises(CannotNotifyError) as error_info:
        async with GeneralErrorNotificator():
            raise InsufficientKeysAutoSignError(MockCommand())

    assert isinstance(error_info.value.error, InsufficientKeysAutoSignError)
    assert error_info.value.reason == InsufficientKeysAutoSignError.REASON
