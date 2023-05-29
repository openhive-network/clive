from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.command import Command
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.storage.mock_database import PrivateKey
from clive.exceptions import CannotActivateError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperRemote
    from clive.__private.core.beekeeper.handle import BeekeeperLocal
    from clive.__private.core.profile_data import ProfileData


@dataclass
class WriteProfileDataToBeekeeper(Command[str]):
    profile_data: ProfileData
    beekeeper: BeekeeperLocal | BeekeeperRemote
    password: str

    def execute(self) -> None:
        wallet_name = self.profile_data.name
        try:
            Activate(beekeeper=self.beekeeper, wallet=wallet_name, password=self.password).execute()
        except CannotActivateError:
            self.password = CreateWallet(
                beekeeper=self.beekeeper, wallet=wallet_name, password=self.password
            ).execute_with_result()

        for i, key in enumerate(self.profile_data.working_account.keys):
            if isinstance(key, PrivateKey):
                self.profile_data.working_account.keys[i] = ImportKey(
                    wallet=wallet_name, key_to_import=key, beekeeper=self.beekeeper
                ).execute_with_result()
