from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.commands.remove_key import RemoveKey
from clive.__private.storage.mock_database import PublicKey, PublicKeyAliased

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive.__private.core.commands.abc.command_observable import SenderT
    from clive.__private.core.profile_data import ProfileData


@dataclass(kw_only=True)
class SyncDataWithBeekeeper(CommandInActive[bool]):
    profile_data: ProfileData
    beekeeper: Beekeeper

    def _execute(self) -> None:
        self.__remove_hanging_keys()
        self.__import_pending_keys()
        self._result = True

    def __remove_hanging_keys(self) -> None:
        wallet_name = self.profile_data.name
        keys_to_keep = self.profile_data.working_account.keys
        keys_in_beekeeper = self.beekeeper.api.get_public_keys().keys

        for key in keys_in_beekeeper:
            if key not in keys_to_keep:
                RemoveKey(
                    app_state=self.app_state, beekeeper=self.beekeeper, wallet=wallet_name, key_to_remove=PublicKey(key)
                ).execute()

    def __import_pending_keys(self) -> None:
        def __on_import_key_result(
                _: SenderT, result: PublicKeyAliased | None, exception: Exception | None  # noqa: ARG001
        ) -> None:
            if result:
                self.profile_data.working_account.keys.append(result)

        for alias, key in self.profile_data.working_account.keys_to_import.items():
            command = ImportKey(
                app_state=self.app_state,
                skip_activate=self.skip_activate,
                wallet=self.profile_data.name,
                alias=alias,
                key_to_import=key,
                beekeeper=self.beekeeper,
            )
            command.observe_result(__on_import_key_result)
            command.execute()
        self.profile_data.working_account.keys_to_import.clear()
