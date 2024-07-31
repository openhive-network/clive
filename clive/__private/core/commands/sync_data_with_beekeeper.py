from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.import_key import ImportKey

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased
    from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class SyncDataWithBeekeeper(CommandInUnlocked, Command):
    profile_data: ProfileData
    beekeeper: Beekeeper

    async def _execute(self) -> None:
        if not self.profile_data.accounts.has_working_account:
            return

        await self.__import_pending_keys()

    async def __import_pending_keys(self) -> None:
        async def import_key(key_to_import: PrivateKeyAliased) -> PublicKeyAliased:
            return await ImportKey(
                app_state=self.app_state,
                wallet=self.profile_data.name,
                key_to_import=key_to_import,
                beekeeper=self.beekeeper,
            ).execute_with_result()

        await self.profile_data.keys.import_pending_to_beekeeper(import_key)
