from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_encryption import CommandEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult


class CommandDecryptError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Failed to decrypt the content.")


@dataclass(kw_only=True)
class Decrypt(CommandEncryption, CommandWithResult[str]):
    encrypted_content: str

    async def _execute(self) -> None:
        from beekeepy.exceptions import CommunicationError

        try:
            encryption_key = await self.encryption_public_key
            self._result = await self.unlocked_encryption_wallet.decrypt_data(
                from_key=encryption_key,
                to_key=encryption_key,
                content=self.encrypted_content,
            )
        except CommunicationError as error:
            raise CommandDecryptError(self) from error
