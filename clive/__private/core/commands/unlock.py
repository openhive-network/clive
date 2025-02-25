from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from beekeepy.exceptions import NoWalletWithSuchNameError

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.create_encryption_wallet import CreateEncryptionWallet
from clive.__private.core.commands.create_user_wallet import CreateUserWallet
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy import AsyncSession, AsyncUnlockedWallet

    from clive.__private.core.app_state import AppState

WalletRecoveryStatus = Literal["nothing_to_recover", "encryption_wallet_recovered", "user_wallet_recovered"]


class CannotRecoverWalletsDuringUnlockError(CommandError):
    MESSAGE: Final[str] = "Looks like beekeeper wallets no longer exist and we cannot do the recovery process."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


@dataclass(kw_only=True)
class Unlock(CommandPasswordSecured, CommandWithResult[WalletRecoveryStatus]):
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

        if not encryption_wallet and not user_wallet:
            # we should not recreate both wallets during the unlock process
            # because when both wallets are deleted, we don't know what the previous password was
            # so this could lead to a situation profile password will be changed when wallets are deleted
            raise CannotRecoverWalletsDuringUnlockError(self)

        self._result = "nothing_to_recover"

        if not encryption_wallet:
            encryption_wallet = await CreateEncryptionWallet(
                session=self.session, profile_name=self.profile_name, password=self.password
            ).execute_with_result()
            self._result = "encryption_wallet_recovered"

        if not user_wallet:
            user_wallet = await CreateUserWallet(
                session=self.session, profile_name=self.profile_name, password=self.password
            ).execute_with_result()
            self._result = "user_wallet_recovered"

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
