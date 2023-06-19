from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.logger import logger
from clive.exceptions import CannotActivateError, CommunicationError

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.beekeeper import Beekeeper


class WalletDoesNotExistsError(CannotActivateError):
    ERROR_MESSAGE: ClassVar[str] = "Assert Exception:wallet->load_wallet_file(): Unable to open file: "


@dataclass(kw_only=True)
class Activate(Command):
    beekeeper: Beekeeper
    wallet: str
    password: str
    time: timedelta | None = None

    def _execute(self) -> None:
        try:
            self.beekeeper.api.open(wallet_name=self.wallet)
            self.beekeeper.api.unlock(wallet_name=self.wallet, password=self.password)
            if self.time is not None:
                SetTimeout(beekeeper=self.beekeeper, seconds=int(self.time.total_seconds())).execute()
        except CommunicationError as error:
            for arg_raw in error.args:
                arg = arg_raw["error"]["message"] if isinstance(arg_raw, dict) else arg_raw
                if WalletDoesNotExistsError.ERROR_MESSAGE in arg:
                    raise WalletDoesNotExistsError(error) from error
            raise CannotActivateError(error) from error

        logger.info("Mode switched to [bold green]active[/].")
