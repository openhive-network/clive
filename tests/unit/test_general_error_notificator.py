from __future__ import annotations

from dataclasses import dataclass

import pytest

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.autosign import AuthorityPrefetchAutoSignError
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator


@dataclass(kw_only=True)
class MockCommand(Command):
    async def _execute(self) -> None:
        """Just a mock command."""


async def test_authority_prefetch_error_is_caught_by_notificator() -> None:
    exception = AuthorityPrefetchAutoSignError(MockCommand(), cause=RuntimeError("node error"))
    notificator = GeneralErrorNotificator()

    assert notificator._is_exception_to_catch(exception), "AuthorityPrefetchAutoSignError should be caught"
    assert notificator._determine_message(exception) == AuthorityPrefetchAutoSignError.REASON


async def test_autosign_errors_raise_cannot_notify_when_tui_not_launched() -> None:
    with pytest.raises(CannotNotifyError) as error_info:
        async with GeneralErrorNotificator():
            raise AuthorityPrefetchAutoSignError(MockCommand(), cause=RuntimeError("node error"))

    assert isinstance(error_info.value.error, AuthorityPrefetchAutoSignError)
    assert error_info.value.reason == AuthorityPrefetchAutoSignError.REASON
