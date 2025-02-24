from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


@dataclass
class CreateWalletResult:
    unlocked_user_wallet: AsyncUnlockedWallet
    unlocked_encryption_wallet: AsyncUnlockedWallet


@dataclass(kw_only=True)
class CreateWallet(CommandWithResult[CreateWalletResult]):
    app_state: AppState | None = None
    session: AsyncSession
    wallet_name: str
    password: str
    unlock_time: timedelta | None = None
    permanent_unlock: bool = True
    """Will take precedence when `unlock_time` is also set."""

    async def _execute(self) -> None:
        unlocked_encryption_wallet = await self.session.create_wallet(
            name=EncryptionService.get_encryption_wallet_name(self.wallet_name), password=self.password
        )
        await unlocked_encryption_wallet.generate_key()

        unlocked_user_wallet = await self.session.create_wallet(name=self.wallet_name, password=self.password)

        self._result = CreateWalletResult(unlocked_user_wallet, unlocked_encryption_wallet)

        if self.app_state:
            await self.app_state.unlock(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))

        await SetTimeout(session=self.session, time=self.unlock_time, permanent=self.permanent_unlock).execute()
