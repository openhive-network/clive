from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass
class SetTimeout(Command[None]):
    beekeeper: Beekeeper
    seconds: int

    def _execute(self) -> None:
        self.beekeeper.api.set_timeout(seconds=self.seconds)
        logger.info(f"Timeout set to {self.seconds} s.")
