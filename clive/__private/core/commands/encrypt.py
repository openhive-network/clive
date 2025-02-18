from __future__ import annotations

from dataclasses import dataclass

from helpy.exceptions import CommunicationError

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_encryption import CommandEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult


class CommandEncryptError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Failed to encrypt the content.")


@dataclass(kw_only=True)
class Encrypt(CommandEncryption, CommandWithResult[str]):
    content: str

    async def _execute(self) -> None:
        try:
            encryption_key = await self.encryption_public_key
            self._result = await self.unlocked_encryption_wallet.encrypt_data(
                from_key=encryption_key,
                to_key=encryption_key,
                content=self.content,
            )
        except CommunicationError as error:
            raise CommandEncryptError(self) from error
