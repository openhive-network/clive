from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.import_key import ImportKey

if TYPE_CHECKING:
    from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased
    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class SyncDataWithBeekeeper(CommandInUnlocked, Command):
    profile: Profile

    async def _execute(self) -> None:
        await self.__import_pending_keys()

    async def __import_pending_keys(self) -> None:
        async def import_key(key_to_import: PrivateKeyAliased) -> PublicKeyAliased:
            return await ImportKey(
                unlocked_wallet=self.unlocked_wallet, key_to_import=key_to_import
            ).execute_with_result()

        await self.profile.keys.import_pending_to_beekeeper(import_key)
