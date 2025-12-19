from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.commands.decrypt_memo import DecodeEncryptedMemoError as CoreDecodeEncryptedMemoError
from clive.__private.core.commands.decrypt_memo import DecryptMemoError as CoreDecryptMemoError


class DecodeEncryptedMemoError(CLIPrettyError):
    def __init__(self, encrypted_memo: str) -> None:
        message = f"Failed to decode encrypted memo. Memo might have invalid format, received: '{encrypted_memo}'"
        super().__init__(message)


class DecryptMemoError(CLIPrettyError):
    def __init__(self) -> None:
        super().__init__("Failed to decrypt memo. You might not have the correct memo key in your wallet.")


@dataclass(kw_only=True)
class Decrypt(WorldBasedCommand):
    """Decrypt and show an encrypted memo using the memo key from the wallet.

    Attributes:
        encrypted_memo: The encrypted memo to decrypt.
    """

    encrypted_memo: str

    async def validate(self) -> None:
        self._validate_encrypted_memo_format()
        await super().validate()

    async def _run(self) -> None:
        try:
            result = await self.world.commands.decrypt_memo(encrypted_memo=self.encrypted_memo)
            decrypted = result.result_or_raise
        except CoreDecodeEncryptedMemoError as error:
            raise DecodeEncryptedMemoError(self.encrypted_memo) from error
        except CoreDecryptMemoError as error:
            raise DecryptMemoError from error

        print_cli(f"Decrypted memo: '{decrypted}'")

    def _validate_encrypted_memo_format(self) -> None:
        if not self.encrypted_memo.startswith("#"):
            raise CLIPrettyError("The memo does not appear to be encrypted. Encrypted memos start with '#'.")
