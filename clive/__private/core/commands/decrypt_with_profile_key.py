from __future__ import annotations

from dataclasses import dataclass

from helpy.exceptions import CommunicationError

from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import CommandDecryptError


@dataclass(kw_only=True)
class DecryptWithProfileKey(CommandProfileEncryption, CommandWithResult[str]):
    encrypted_content: str

    async def _execute(self) -> None:
        try:
            encryption_key = await self.encryption_public_key
            self._result = await self.unlocked_profile_encryption_wallet.decrypt_data(
                from_key=encryption_key,
                to_key=encryption_key,
                content=self.encrypted_content,
            )
        except CommunicationError as error:
            raise CommandDecryptError(self) from error
