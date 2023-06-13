from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.commands.command_in_active import CommandInActive
from clive.__private.core.commands.import_key import ImportKey

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData


@dataclass
class WriteProfileDataToBeekeeper(CommandInActive[None]):
    profile_data: ProfileData
    wallet: str = field(init=False)

    def __post_init__(self) -> None:
        self.wallet = self.profile_data.name

    def _execute(self) -> None:
        for alias, key in self.profile_data.working_account.keys_to_import.items():
            imported = ImportKey(
                wallet=self.wallet, alias=alias, key_to_import=key, beekeeper=self.beekeeper
            ).execute_with_result()
            self.profile_data.working_account.keys.append(imported)
        self.profile_data.working_account.keys_to_import.clear()
