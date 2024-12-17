from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.decrypt_with_profile_key import DecryptWithProfileKey
from clive.__private.core.commands.encrypt_with_profile_key import EncryptWithProfileKey

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


class EncryptionService:
    def __init__(self, beekeeper: Beekeeper) -> None:
        assert beekeeper.is_running, "Encryption service requires running beekeeper."
        self._beekeeper = beekeeper

    async def decrypt(self, encrypted_content: str) -> str:
        return await DecryptWithProfileKey(
            beekeeper=self._beekeeper,
            encrypted_content=encrypted_content,
        ).execute_with_result()

    async def encrypt(self, content: str) -> str:
        return await EncryptWithProfileKey(
            beekeeper=self._beekeeper,
            content=content,
        ).execute_with_result()
