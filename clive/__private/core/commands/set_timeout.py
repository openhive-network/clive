from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from beekeepy import AsyncSession


@dataclass(kw_only=True)
class SetTimeout(Command):
    session: AsyncSession
    seconds: int

    async def _execute(self) -> None:
        await self.session.set_timeout(seconds=self.seconds)
        logger.info(f"Timeout set to {self.seconds} s.")
