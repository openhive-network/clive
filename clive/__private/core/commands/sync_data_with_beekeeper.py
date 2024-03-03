from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.import_key import ImportKey
from clive.models.aliased import UnlockedWallet

if TYPE_CHECKING:
    from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased
    from clive.__private.core.profile_data import ProfileData
    from clive.models.aliased import Wallet


@dataclass(kw_only=True)
class SyncDataWithBeekeeper(CommandInActive, Command):
    profile_data: ProfileData
    wallet: UnlockedWallet | Wallet

    async def _execute(self) -> None:
        if not self.profile_data.is_working_account_set():
            return

        await self.__import_pending_keys()

    async def __import_pending_keys(self) -> None:
        async def import_key(key_to_import: PrivateKeyAliased) -> PublicKeyAliased:
            wallet: Wallet | UnlockedWallet | None = self.wallet
            if wallet is not None and not isinstance(wallet, UnlockedWallet):
                wallet = await wallet.unlocked
                assert wallet is not None, "Wallet is not unlocked!"
            assert isinstance(wallet, UnlockedWallet)
            return await ImportKey(
                app_state=self.app_state,
                wallet=wallet,
                key_to_import=key_to_import,
            ).execute_with_result()

        await self.profile_data.working_account.keys.import_pending_to_beekeeper(import_key)
