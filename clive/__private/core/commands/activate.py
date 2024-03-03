from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from beekeepy._interface.exceptions import NoWalletWithSuchNameError

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured, InvalidPasswordError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.exceptions import CannotActivateError, CommunicationError, KnownError
from clive.models.aliased import UnlockedWallet

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.app_state import AppState
    from clive.models.aliased import Session


class ActivateInvalidPasswordError(InvalidPasswordError, CannotActivateError):
    pass


@dataclass(kw_only=True)
class Activate(CommandPasswordSecured, CommandWithResult[UnlockedWallet]):
    app_state: AppState
    session: Session
    wallet: str
    time: timedelta | None = None
    permanent: bool = False

    __KNOWN_ERRORS: Final[tuple[type[KnownError], ...]] = (NoWalletWithSuchNameError, ActivateInvalidPasswordError) # type: ignore

    async def _execute(self) -> None:
        try:
            self._result = await (await self.session.open_wallet(name=self.wallet)).unlock(password=self.password)
            if activation_seconds := self.__get_activation_seconds():
                await SetTimeout(session=self.session, seconds=activation_seconds).execute()
        except NoWalletWithSuchNameError:
            raise
        except (CommunicationError) as error:
            for known_error in self.__KNOWN_ERRORS:
                if known_error.ERROR_MESSAGE in str(error):
                    raise known_error(error) from error
            raise CannotActivateError(error) from error

        self.app_state.activate()

    def __get_activation_seconds(self) -> int | None:
        if self.permanent:
            # beekeeper does not support permanent activation in a convenient way, we have to pass a very big number
            # which is uint32 max value
            return 2**32 - 1

        if self.time is None:
            return None

        return int(self.time.total_seconds())
