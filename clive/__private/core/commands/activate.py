from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger
from clive.exceptions import CannotActivateError, CommunicationError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperRemote


@dataclass
class Activate(Command[None]):
    beekeeper: BeekeeperRemote
    wallet: str
    password: str

    def execute(self) -> None:
        try:
            self.beekeeper.api.open(wallet_name=self.wallet)
            self.beekeeper.api.unlock(wallet_name=self.wallet, password=self.password)
        except CommunicationError as e:
            raise CannotActivateError(e) from e

        logger.info("Mode switched to [bold green]active[/].")
