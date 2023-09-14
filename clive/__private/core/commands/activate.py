from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.exceptions import CannotActivateError, CommunicationError

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper import Beekeeper


class WalletDoesNotExistsError(CannotActivateError):
    ERROR_MESSAGE: ClassVar[str] = "Assert Exception:wallet->load_wallet_file(): Unable to open file: "


@dataclass(kw_only=True)
class Activate(CommandPasswordSecured):
    app_state: AppState
    beekeeper: Beekeeper
    wallet: str
    time: timedelta | None = None
    permanent: bool = False

    async def _execute(self) -> None:
        try:
            await self.beekeeper.api.unlock(wallet_name=self.wallet, password=self.password)
            if activation_seconds := self.__get_activation_seconds():
                await SetTimeout(beekeeper=self.beekeeper, seconds=activation_seconds).execute()
        except CommunicationError as error:
            for arg_raw in error.args:
                arg = arg_raw["error"]["message"] if isinstance(arg_raw, dict) else arg_raw
                if WalletDoesNotExistsError.ERROR_MESSAGE in arg:
                    raise WalletDoesNotExistsError(error) from error
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
