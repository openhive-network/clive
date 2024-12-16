from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.get_unlocked_profile_name import GetUnlockedProfileName


@dataclass(kw_only=True)
class EncryptWithProfileKey(CommandProfileEncryption, CommandWithResult[str]):
    content: str

    async def _execute(self) -> None:
        profile_name = await GetUnlockedProfileName(beekeeper=self.beekeeper).execute_with_result()
        encryption_key = await self.get_encryption_public_key(profile_name)
        wrapper = await self.beekeeper.api.encrypt_data(
            wallet_name=self.get_wallet_name(profile_name=profile_name),
            from_public_key=encryption_key.public_key,
            to_public_key=encryption_key.public_key,
            content=self.content,
        )
        self._result = wrapper.encrypted_content
