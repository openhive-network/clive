from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class LockAll(Command):
    app_state: AppState | None = None
    beekeeper: Beekeeper

    async def _execute(self) -> None:
        await self.beekeeper.api.lock_all()
        logger.info("All wallets have been locked.")
