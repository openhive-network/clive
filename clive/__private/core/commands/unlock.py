from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.set_timeout import SetTimeout

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession

    from clive import World
    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Unlock(CommandPasswordSecured):
    app_state: AppState | None = None
    session: AsyncSession
    wallet_name: str
    time: timedelta | None = None
    permanent: bool = False
    world: World | None = None

    async def _execute(self) -> None:
        if unlock_seconds := self.__get_unlock_seconds():
            await SetTimeout(session=self.session, seconds=unlock_seconds).execute()

        locked_wallet = await self.session.open_wallet(name=self.wallet_name)
        unlocked_wallet = await locked_wallet.unlock(password=self.password)
        if self.world is not None:
            await self.world._set_unlocked_wallet(unlocked_wallet)
        if self.app_state is not None:
            self.app_state.unlock()

    def __get_unlock_seconds(self) -> int | None:
        if self.permanent:
            # beekeeper does not support permanent unlock in a convenient way, we have to pass a very big number
            # which is uint32 max value
            return 2**32 - 1

        if self.time is None:
            return None

        return int(self.time.total_seconds())
