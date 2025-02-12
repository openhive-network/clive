from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.encryption_helpers import get_encryption_wallet_name

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Unlock(CommandPasswordSecured):
    app_state: AppState | None = None
    session: AsyncSession
    wallet_name: str
    time: timedelta | None = None
    permanent: bool = False

    async def _execute(self) -> None:
        if unlock_seconds := self.__get_unlock_seconds():
            await SetTimeout(session=self.session, seconds=unlock_seconds).execute()

        unlocked_wallet = await (await self.session.open_wallet(name=self.wallet_name)).unlock(password=self.password)
        unlocked_profile_encryption_wallet = await (
            await self.session.open_wallet(name=get_encryption_wallet_name(self.wallet_name))
        ).unlock(password=self.password)
        if self.app_state is not None:
            await self.app_state.unlock((unlocked_wallet, unlocked_profile_encryption_wallet))

    def __get_unlock_seconds(self) -> int | None:
        if self.permanent:
            # beekeeper does not support permanent unlock in a convenient way, we have to pass a very big number
            # which is uint32 max value
            return 2**32 - 1

        if self.time is None:
            return None

        return int(self.time.total_seconds())
