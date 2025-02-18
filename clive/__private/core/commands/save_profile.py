from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryption
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class SaveProfile(CommandProfileEncryption, Command):
    profile: Profile

    async def _execute(self) -> None:
        if self.profile.is_skip_saving:
            return
        encryption_service = EncryptionService(WalletContainer(self.unlocked_wallet, self.unlocked_encryption_wallet))
        await self.profile.save(encryption_service)

    async def _is_execution_possible(self) -> bool:
        return self.profile.is_skip_saving or await super()._is_execution_possible()
