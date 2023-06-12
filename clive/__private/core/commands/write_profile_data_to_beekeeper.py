from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate, WalletDoesNotExistsError
from clive.__private.core.commands.command import Command
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.import_key import ImportKey

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.profile_data import ProfileData


@dataclass
class WriteProfileDataToBeekeeper(Command[None]):
    profile_data: ProfileData
    beekeeper: Beekeeper
    password: str

    def execute(self) -> None:
        wallet_name = self.profile_data.name
        try:
            Activate(beekeeper=self.beekeeper, wallet=wallet_name, password=self.password).execute()
        except WalletDoesNotExistsError:
            self.password = CreateWallet(
                beekeeper=self.beekeeper, wallet=wallet_name, password=self.password
            ).execute_with_result()

        for alias, key in self.profile_data.working_account.keys_to_import.items():
            imported = ImportKey(
                wallet=wallet_name, alias=alias, key_to_import=key, beekeeper=self.beekeeper
            ).execute_with_result()
            self.profile_data.working_account.keys.append(imported)
        self.profile_data.working_account.keys_to_import.clear()
