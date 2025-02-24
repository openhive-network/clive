from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.create_encryption_wallet import CreateEncryptionWallet
from clive.__private.core.commands.create_user_wallet import CreateUserWallet
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


@dataclass
class CreateProfileWalletsResult:
    unlocked_user_wallet: AsyncUnlockedWallet
    unlocked_encryption_wallet: AsyncUnlockedWallet


@dataclass(kw_only=True)
class CreateProfileWallets(CommandWithResult[CreateProfileWalletsResult]):
    app_state: AppState | None = None
    session: AsyncSession
    profile_name: str
    password: str
    unlock_time: timedelta | None = None
    permanent_unlock: bool = True
    """Will take precedence when `unlock_time` is also set."""

    async def _execute(self) -> None:
        unlocked_encryption_wallet = await CreateEncryptionWallet(
            session=self.session, profile_name=self.profile_name, password=self.password
        ).execute_with_result()

        unlocked_user_wallet = await CreateUserWallet(
            session=self.session, profile_name=self.profile_name, password=self.password
        ).execute_with_result()

        self._result = CreateProfileWalletsResult(unlocked_user_wallet, unlocked_encryption_wallet)

        if self.app_state:
            await self.app_state.unlock(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))

        await SetTimeout(session=self.session, time=self.unlock_time, permanent=self.permanent_unlock).execute()
