from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryption
from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class SaveProfile(CommandProfileEncryption, Command):
    profile: Profile

    async def _execute(self) -> None:
        encryption_service = EncryptionService(self.unlocked_profile_encryption_wallet)
        await self.profile.save(encryption_service)
