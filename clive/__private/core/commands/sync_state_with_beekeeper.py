from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from beekeepy import AsyncWallet

    from clive.__private.core.app_state import AppState, LockSource


class InvalidWalletStateError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(
            command, "There should be unlocked wallet with blockchain keys and unlocked profile encryption wallet."
        )


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    user_wallet: AsyncWallet
    encryption_wallet: AsyncWallet
    app_state: AppState
    source: LockSource = "unknown"

    async def _execute(self) -> None:
        await self.__sync_state()

    async def __sync_state(self) -> None:
        unlocked_user_wallet = await self.user_wallet.unlocked
        unlocked_encryption_wallet = await self.encryption_wallet.unlocked

        if unlocked_user_wallet is not None and unlocked_encryption_wallet is not None:
            await self.app_state.unlock(WalletContainer(unlocked_user_wallet, unlocked_encryption_wallet))
        elif unlocked_user_wallet is None and unlocked_encryption_wallet is None:
            self.app_state.lock(self.source)
        else:
            raise InvalidWalletStateError(self)
