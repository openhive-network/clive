from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.commands.abc.command_encryption import CommandEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.types import MigrationStatus
from clive.__private.core.wallet_container import WalletContainer
from clive.__private.storage.service.service import PersistentStorageService


@dataclass(kw_only=True)
class MigrateProfile(CommandEncryption, CommandWithResult[MigrationStatus]):
    profile_name: str

    async def _execute(self) -> None:
        encryption_service = EncryptionService(WalletContainer(self.unlocked_wallet, self.unlocked_encryption_wallet))
        self._result = await PersistentStorageService(encryption_service).migrate(self.profile_name)
