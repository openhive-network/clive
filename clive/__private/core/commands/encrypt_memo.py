from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import beekeepy.exceptions as bke

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from wax import encode_encrypted_memo as wax_encode_encrypted_memo
from wax._private.result_tools import to_cpp_string, to_python_string

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKey


class EncryptMemoKeyNotImportedError(CommandError):
    def __init__(self, command: Command) -> None:
        message = "Failed to encrypt the memo because the memo key is not imported."
        super().__init__(command, message)


@dataclass(kw_only=True)
class EncryptMemo(CommandInUnlocked, CommandWithResult[str]):
    """
    Encrypt a memo using the memo keys.

    Attributes:
        content: The memo content to encrypt (should start with '#').
        from_key: The sender's memo public key.
        to_key: The recipient's memo public key.
    """

    content: str
    from_key: PublicKey
    to_key: PublicKey

    async def _execute(self) -> None:
        try:
            # Encrypt the content using beekeeper
            encrypted_content = await self.unlocked_wallet.encrypt_data(
                from_key=self.from_key.value,
                to_key=self.to_key.value,
                content=self.content,
            )
        except bke.NotExistingKeyError as error:
            raise EncryptMemoKeyNotImportedError(self) from error

        # Encode the encrypted memo with keys using wax
        encoded_memo = wax_encode_encrypted_memo(
            to_cpp_string(encrypted_content),
            to_cpp_string(self.from_key.value),
            to_cpp_string(self.to_key.value),
        )
        self._result = to_python_string(encoded_memo)
