from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import BeekeeperRemote


class Activate(Command[None]):
    def __init__(
        self,
        beekeeper: BeekeeperRemote,
        *,
        wallet: str,
        password: str,
    ) -> None:
        super().__init__(result_default=None)
        self.__beekeeper = beekeeper
        self.__wallet = wallet
        self.__password = password

    def execute(self) -> None:
        self.__beekeeper.api.open(wallet_name=self.__wallet)
        self.__beekeeper.api.unlock(wallet_name=self.__wallet, password=self.__password)
        logger.info("Mode switched to [bold green]active[/].")
