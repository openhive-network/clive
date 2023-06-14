from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class Deactivate(Command[None]):
    beekeeper: Beekeeper
    wallet: str

    def _execute(self) -> None:
        self.beekeeper.api.lock(wallet_name=self.wallet)
        logger.info("Deactivated")
