from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.create_encryption_wallet import CreateEncryptionWallet
from clive.__private.core.commands.create_user_wallet import CreateUserWallet

if TYPE_CHECKING:
    from beekeepy.asynchronous import AsyncSession, AsyncUnlockedWallet

RecoverWalletsStatus = Literal["nothing_recovered", "encryption_wallet_recovered", "user_wallet_recovered"]


class CannotRecoverWalletsError(CommandError):
    MESSAGE: Final[str] = "Looks like beekeeper wallets no longer exist and we cannot do the recovery process."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


@dataclass
class RecoverWalletsResult:
    status: RecoverWalletsStatus = "nothing_recovered"
    recovered_wallet: AsyncUnlockedWallet | None = None


@dataclass(kw_only=True)
class RecoverWallets(CommandPasswordSecured, CommandWithResult[RecoverWalletsResult]):
    """
    Recover (if possible) the profile-related wallets (user wallet and encryption wallet) managed by the beekeeper.

    Note that only one wallet can be recovered. If both wallets are missing, the recovery process will fail.

    Attributes:
        profile_name: The name of the profile for which wallets are to be recovered.
        session: The beekeeper session to interact with.
        should_recover_encryption_wallet: Flag indicating whether to recover the encryption wallet.
        should_recover_user_wallet: Flag indicating whether to recover the user wallet.
    """

    profile_name: str
    session: AsyncSession
    should_recover_encryption_wallet: bool = False
    should_recover_user_wallet: bool = False

    async def _execute(self) -> None:
        self._validate_recovery_attempt()
        status, wallet = await self._recover_wallet()
        self._result = RecoverWalletsResult(status, wallet)

    def _validate_recovery_attempt(self) -> None:
        """
        Ensure that both wallets are not recovered simultaneously.

        We should not recreate both wallets during the unlock process  because when both wallets are deleted,
        we don't know what the previous password was so this could lead to a situation profile password will be changed
        when wallets are deleted.
        """
        if self.should_recover_encryption_wallet and self.should_recover_user_wallet:
            raise CannotRecoverWalletsError(self)

    async def _recover_wallet(self) -> tuple[RecoverWalletsStatus, AsyncUnlockedWallet | None]:
        """Attempt to recover a wallet."""
        if self.should_recover_encryption_wallet:
            return await self._recover_encryption_wallet()
        if self.should_recover_user_wallet:
            return await self._recover_user_wallet()
        return "nothing_recovered", None

    async def _recover_encryption_wallet(self) -> tuple[RecoverWalletsStatus, AsyncUnlockedWallet]:
        """Handle encryption wallet recovery."""
        wallet = await CreateEncryptionWallet(
            session=self.session, profile_name=self.profile_name, password=self.password
        ).execute_with_result()
        return "encryption_wallet_recovered", wallet

    async def _recover_user_wallet(self) -> tuple[RecoverWalletsStatus, AsyncUnlockedWallet]:
        """Handle user wallet recovery."""
        wallet = await CreateUserWallet(
            session=self.session, profile_name=self.profile_name, password=self.password
        ).execute_with_result()
        return "user_wallet_recovered", wallet
