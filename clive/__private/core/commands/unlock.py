from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import NoWalletWithSuchNameError

from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.recover_wallets import RecoverWallets, RecoverWalletsStatus
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class Unlock(CommandPasswordSecured, CommandWithResult[RecoverWalletsStatus]):
    """Unlock the profile-related wallets (user keys and encryption key) managed by the beekeeper."""

    profile_name: str
    session: AsyncSession
    time: timedelta | None = None
    permanent: bool = True
    """Will take precedence when `time` is also set."""
    app_state: AppState | None = None

    async def _execute(self) -> None:
        await SetTimeout(session=self.session, time=self.time, permanent=self.permanent).execute()

        encryption_wallet = await self._unlock_wallet(EncryptionService.get_encryption_wallet_name(self.profile_name))
        user_wallet = await self._unlock_wallet(self.profile_name)
        is_encryption_wallet_missing = encryption_wallet is None
        is_user_wallet_missing = user_wallet is None

        recover_wallets_result = await RecoverWallets(
            password=self.password,
            profile_name=self.profile_name,
            session=self.session,
            should_recover_encryption_wallet=is_encryption_wallet_missing,
            should_recover_user_wallet=is_user_wallet_missing,
        ).execute_with_result()

        self._result = recover_wallets_result.status

        if self._result == "encryption_wallet_recovered":
            encryption_wallet = recover_wallets_result.recovered_wallet
        elif self._result == "user_wallet_recovered":
            user_wallet = recover_wallets_result.recovered_wallet

        assert user_wallet is not None, "User wallet should be created at this point"
        assert encryption_wallet is not None, "Encryption wallet should be created at this point"

        if self.app_state is not None:
            await self.app_state.unlock(WalletContainer(user_wallet, encryption_wallet))

    async def _unlock_wallet(self, name: str) -> AsyncUnlockedWallet | None:
        try:
            wallet = await self.session.open_wallet(name=name)
        except NoWalletWithSuchNameError:
            return None
        return await wallet.unlock(password=self.password)
