from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.constants.env import WALLETS_AMOUNT_PER_PROFILE
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from beekeepy import AsyncSession

    from clive.__private.core.app_state import AppState, LockSource


class InvalidWalletAmountError(CommandError):
    MESSAGE: Final[str] = (
        "The amount of wallets is invalid. "
        f"Profile can have either 0 (if not created yet) or {WALLETS_AMOUNT_PER_PROFILE} wallets."
    )

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


class InvalidWalletStateError(CommandError):
    MESSAGE: Final[str] = (
        "The user wallet, containing its keys, and the encryption wallet must BOTH be unlocked or locked. "
        "When they have different states, something went wrong."
    )

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    session: AsyncSession
    app_state: AppState
    source: LockSource = "unknown"

    async def _execute(self) -> None:
        await self.__sync_state()

    async def __sync_state(self) -> None:
        wallets = await self.session.wallets_unlocked

        if len(wallets) not in [0, WALLETS_AMOUNT_PER_PROFILE]:
            raise InvalidWalletAmountError(self)

        user_wallet = next(
            (wallet for wallet in wallets if not EncryptionService.is_encryption_wallet_name(wallet.name)), None
        )
        encryption_wallet = next(
            (wallet for wallet in wallets if EncryptionService.is_encryption_wallet_name(wallet.name)), None
        )

        if user_wallet and encryption_wallet:
            await self.app_state.unlock(WalletContainer(user_wallet, encryption_wallet))
        elif not user_wallet and not encryption_wallet:
            self.app_state.lock(self.source)
        else:
            raise InvalidWalletStateError(self)
