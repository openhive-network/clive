from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.logger import logger

if TYPE_CHECKING:
    from beekeepy import AsyncSession


@dataclass(kw_only=True)
class SetTimeout(Command):
    session: AsyncSession
    time: timedelta | None = None
    permanent: bool = False
    """Will take precedence when `time` is also set."""

    async def _execute(self) -> None:
        timeout_in_seconds = self._determine_timeout().total_seconds()
        await self.session.set_timeout(seconds=int(timeout_in_seconds))
        logger.info(f"Timeout set to {timeout_in_seconds} s.")

    def _determine_timeout(self) -> timedelta:
        if self.permanent:
            # beekeeper does not support permanent timeout in a convenient way, we have to pass a very big number
            # which is uint32 max value
            return timedelta(seconds=2**32 - 1)

        assert self.time is not None, "`time` can't be none if `permanent` is set to False."
        return self.time
