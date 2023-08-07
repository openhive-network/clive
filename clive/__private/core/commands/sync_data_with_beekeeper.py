from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class SyncDataWithBeekeeper(CommandInActive, Command):
    profile_data: ProfileData
    beekeeper: Beekeeper

    async def _async_execute(self) -> None:
        if not self.profile_data.is_working_account_set():
            return

        await self.__import_pending_keys()
        await self.__sync_missing_keys()

    async def __import_pending_keys(self) -> None:
        async def import_key(key_to_import: PrivateKeyAliased) -> PublicKeyAliased:
            return await ImportKey(
                app_state=self.app_state,
                wallet=self.profile_data.name,
                key_to_import=key_to_import,
                beekeeper=self.beekeeper,
            ).async_execute_with_result()

        await self.profile_data.working_account.keys.import_pending_to_beekeeper(import_key)

    async def __sync_missing_keys(self) -> None:
        keys_in_clive = self.profile_data.working_account.keys
        keys_in_beekeeper = self.beekeeper.api.get_public_keys().keys

        keys_missing_in_clive = [key for key in keys_in_beekeeper if key not in keys_in_clive]

        self.profile_data.working_account.keys.add(
            *[PublicKeyAliased(value=key, alias=key) for key in keys_missing_in_clive]
        )
