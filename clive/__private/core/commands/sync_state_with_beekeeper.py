from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from beekeepy import AsyncWallet

    from clive.__private.core.app_state import AppState, LockSource


@dataclass(kw_only=True)
class SyncStateWithBeekeeper(Command):
    wallet: AsyncWallet
    profile_encryption_wallet: AsyncWallet
    app_state: AppState
    source: LockSource = "unknown"

    async def _execute(self) -> None:
        await self.__sync_state()

    async def __sync_state(self) -> None:
        unlocked_wallet = await self.wallet.unlocked
        unlocked_profile_encryption_wallet = await self.profile_encryption_wallet.unlocked
        if unlocked_wallet is not None and unlocked_profile_encryption_wallet is not None:
            wallets = WalletContainer(
                blockchain_keys=unlocked_wallet, profile_encryption=unlocked_profile_encryption_wallet
            )
            await self.app_state.unlock(wallets)
        else:
            self.app_state.lock(self.source)
