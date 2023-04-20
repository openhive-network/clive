from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import BeekeeperRemote


class Deactivate(Command[None]):
    def __init__(self, beekeeper: BeekeeperRemote, *, wallet: str) -> None:
        super().__init__(result_default=None)
        self.__beekeeper = beekeeper
        self.__wallet = wallet

    def execute(self) -> None:
        self.__beekeeper.api.lock(wallet_name=self.__wallet)
        logger.info("Deactivated")
