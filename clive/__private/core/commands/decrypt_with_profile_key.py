from __future__ import annotations

from dataclasses import dataclass

from helpy.exceptions import CommunicationError

from clive.__private.core.commands.abc.command_encryption import CommandEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import CommandDecryptError


@dataclass(kw_only=True)
class DecryptWithProfileKey(CommandEncryption, CommandWithResult[str]):
    encrypted_content: str

    async def _execute(self) -> None:
        try:
            encryption_key = await self.encryption_public_key
            self._result = await self.unlocked_encryption_wallet.decrypt_data(
                from_key=encryption_key,
                to_key=encryption_key,
                content=self.encrypted_content,
            )
        except CommunicationError as error:
            raise CommandDecryptError(self) from error
