from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState, LockSource
    from clive.__private.core.wallet_container import WalletContainer


class InvalidWalletStateError(CommandError):
    MESSAGE: Final[str] = (
        "The user wallet, containing its keys, and the encryption wallet must BOTH be unlocked or locked. "
        "When they have different states, something went wrong."
    )

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.MESSAGE)


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    wallets: WalletContainer
    app_state: AppState
    source: LockSource = "unknown"

    async def _execute(self) -> None:
        await self.__sync_state()

    async def __sync_state(self) -> None:
        wallets = self.wallets
        is_user_wallet_unlocked = await wallets.user_wallet.is_unlocked()
        is_encryption_wallet_unlocked = await wallets.encryption_wallet.is_unlocked()

        if is_user_wallet_unlocked and is_encryption_wallet_unlocked:
            await self.app_state.unlock(wallets)
        elif not is_user_wallet_unlocked and not is_encryption_wallet_unlocked:
            self.app_state.lock(self.source)
        else:
            raise InvalidWalletStateError(self)
