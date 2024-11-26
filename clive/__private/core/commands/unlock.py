from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured, InvalidPasswordError
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.exceptions import CannotUnlockError, CommunicationError, KnownError

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper import Beekeeper


class WalletDoesNotExistsError(KnownError, CannotUnlockError):
    ERROR_MESSAGE: ClassVar[str] = "Unable to open file: "


class UnlockInvalidPasswordError(InvalidPasswordError, CannotUnlockError):
    pass


@dataclass(kw_only=True)
class Unlock(CommandPasswordSecured):
    app_state: AppState | None = None
    beekeeper: Beekeeper
    wallet: str
    time: timedelta | None = None
    permanent: bool = False

    __KNOWN_ERRORS: Final[tuple[type[KnownError], ...]] = (WalletDoesNotExistsError, UnlockInvalidPasswordError)

    async def _execute(self) -> None:
        try:
            await self.beekeeper.api.unlock(wallet_name=self.wallet, password=self.password)
            if unlock_seconds := self.__get_unlock_seconds():
                await SetTimeout(beekeeper=self.beekeeper, seconds=unlock_seconds).execute()
        except CommunicationError as error:
            for known_error in self.__KNOWN_ERRORS:
                if known_error.ERROR_MESSAGE in str(error):
                    raise known_error(error) from error
            raise CannotUnlockError(error) from error

        if self.app_state:
            self.app_state.unlock()

    def __get_unlock_seconds(self) -> int | None:
        if self.permanent:
            # beekeeper does not support permanent unlock in a convenient way, we have to pass a very big number
            # which is uint32 max value
            return 2**32 - 1

        if self.time is None:
            return None

        return int(self.time.total_seconds())
