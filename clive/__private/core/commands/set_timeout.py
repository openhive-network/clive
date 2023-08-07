from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class SetTimeout(Command):
    beekeeper: Beekeeper
    seconds: int

    async def _async_execute(self) -> None:
        self.beekeeper.api.set_timeout(seconds=self.seconds)
        logger.info(f"Timeout set to {self.seconds} s.")
