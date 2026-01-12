from __future__ import annotations

from dataclasses import dataclass

import beekeepy.exceptions as bke

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.keys import PublicKey
from wax import decode_encrypted_memo as wax_decode_encrypted_memo
from wax._private.result_tools import to_cpp_string, to_python_string


class DecodeEncryptedMemoError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Failed to decode the memo.")


class DecryptMemoKeyNotImportedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Failed to decrypt the memo because the memo key was not found in wallet.")


@dataclass(kw_only=True)
class DecryptMemo(CommandInUnlocked, CommandWithResult[str]):
    """
    Decrypt an encrypted memo using the memo key.

    Attributes:
        encrypted_memo: The encrypted memo (should start with '#').
    """

    encrypted_memo: str

    async def _execute(self) -> None:
        try:
            # Decode the encrypted memo to extract keys and content
            decoded = wax_decode_encrypted_memo(to_cpp_string(self.encrypted_memo))
        except RuntimeError as error:
            if "Could not load the crypto memo" in str(error):
                raise DecodeEncryptedMemoError(self) from error
            raise

        from_key = PublicKey.create(to_python_string(decoded.main_encryption_key))
        to_key = PublicKey.create(to_python_string(decoded.other_encryption_key))
        encrypted_content = to_python_string(decoded.encrypted_content)
        try:
            # Decrypt using beekeeper
            decrypted = await self.unlocked_wallet.decrypt_data(
                from_key=from_key.value,
                to_key=to_key.value,
                content=encrypted_content,
            )
        except bke.ErrorInResponseError as error:
            if "Decryption failed" in str(error):
                raise DecryptMemoKeyNotImportedError(self) from error
            raise

        # Remove the leading '#' if present (it's part of the original content)
        self._result = decrypted.removeprefix("#")
