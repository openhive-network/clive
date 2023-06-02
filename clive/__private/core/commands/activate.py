from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.command import Command
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.logger import logger
from clive.exceptions import CannotActivateError, CommunicationError

if TYPE_CHECKING:
    from datetime import timedelta

    from clive.__private.core.beekeeper import Beekeeper


class WalletDoesNotExistsError(CannotActivateError):
    ERROR_MESSAGE: ClassVar[str] = "Assert Exception:wallet->load_wallet_file(): Unable to open file: "


@dataclass
class Activate(Command[None]):
    beekeeper: Beekeeper
    wallet: str
    password: str
    time: timedelta | None = None

    def execute(self) -> None:
        try:
            self.beekeeper.api.open(wallet_name=self.wallet)
            self.beekeeper.api.unlock(wallet_name=self.wallet, password=self.password)
            if self.time is not None:
                SetTimeout(self.beekeeper, int(self.time.total_seconds())).execute()
        except CommunicationError as e:
            if WalletDoesNotExistsError.ERROR_MESSAGE in e.args[1]["error"]["message"]:
                raise WalletDoesNotExistsError(e) from e
            raise CannotActivateError(e) from e

        logger.info("Mode switched to [bold green]active[/].")
