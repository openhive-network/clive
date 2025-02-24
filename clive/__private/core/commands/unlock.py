from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import NoWalletWithSuchNameError

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
    permanent: bool = True
    """Will take precedence when `time` is also set."""
    app_state: AppState | None = None

    async def _execute(self) -> None:
        await SetTimeout(session=self.session, time=self.time, permanent=self.permanent).execute()

        unlocked_encryption_wallet = await (
            await self.session.open_wallet(name=EncryptionService.get_encryption_wallet_name(self.profile_name))
        ).unlock(password=self.password)

        try:
            user_wallet = await self.session.open_wallet(name=self.profile_name)
        except NoWalletWithSuchNameError:
            # create the user wallet if it's missing
            unlocked_user_wallet = await self.session.create_wallet(name=self.profile_name, password=self.password)
        else:
            unlocked_user_wallet = await user_wallet.unlock(password=self.password)

        if self.app_state is not None:
            await self.app_state.unlock(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))
