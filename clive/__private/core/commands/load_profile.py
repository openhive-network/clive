from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.profile import Profile
from clive.__private.core.wallet_container import WalletContainer


@dataclass(kw_only=True)
class LoadProfile(CommandProfileEncryption, CommandWithResult[Profile]):
    profile_name: str

    async def _execute(self) -> None:
        encryption_service = EncryptionService(WalletContainer(self.unlocked_wallet, self.unlocked_encryption_wallet))
        self._result = await Profile.load(self.profile_name, encryption_service)
