from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Unlock(CommandPasswordSecured):
    """Unlock the profile-related wallets (user keys and encryption key) managed by the beekeeper."""

    profile_name: str
    session: AsyncSession
    time: timedelta | None = None
    permanent: bool = False
    app_state: AppState | None = None

    async def _execute(self) -> None:
        if unlock_seconds := self.__get_unlock_seconds():
            await SetTimeout(session=self.session, seconds=unlock_seconds).execute()

        user_keys_wallet = await (await self.session.open_wallet(name=self.profile_name)).unlock(password=self.password)
        encryption_key_wallet = await (
            await self.session.open_wallet(name=EncryptionService.get_encryption_wallet_name(self.profile_name))
        ).unlock(password=self.password)

        if self.app_state is not None:
            wallets = WalletContainer(user_wallet=user_keys_wallet, encryption_wallet=encryption_key_wallet)
            await self.app_state.unlock(wallets)

    def __get_unlock_seconds(self) -> int | None:
        if self.permanent:
            # beekeeper does not support permanent unlock in a convenient way, we have to pass a very big number
            # which is uint32 max value
            return 2**32 - 1

        if self.time is None:
            return None

        return int(self.time.total_seconds())
