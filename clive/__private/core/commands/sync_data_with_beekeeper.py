from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.storage.mock_database import PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class SyncDataWithBeekeeper(CommandInActive, Command):
    profile_data: ProfileData
    beekeeper: Beekeeper

    def _execute(self) -> None:
        self.__import_pending_keys()
        self.__sync_missing_keys()

    def __import_pending_keys(self) -> None:
        for alias, key in self.profile_data.working_account.keys_to_import.items():
            imported = ImportKey(
                app_state=self.app_state,
                wallet=self.profile_data.name,
                alias=alias,
                key_to_import=key,
                beekeeper=self.beekeeper,
            ).execute_with_result()
            self.profile_data.working_account.keys.append(imported)
        self.profile_data.working_account.keys_to_import.clear()

    def __sync_missing_keys(self) -> None:
        keys_in_clive = self.profile_data.working_account.keys
        keys_in_beekeeper = self.beekeeper.api.get_public_keys().keys

        keys_missing_in_clive = [key for key in keys_in_beekeeper if key not in keys_in_clive]

        self.profile_data.working_account.keys.extend(
            PublicKeyAliased(value=key, alias=key) for key in keys_missing_in_clive
        )
