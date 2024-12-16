from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.decrypt_with_profile_key import DecryptWithProfileKey
from clive.__private.core.commands.encrypt_with_profile_key import EncryptWithProfileKey
from clive.__private.core.commands.get_unlocked_profile_name import GetUnlockedProfileName

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


class EncryptionService:
    def __init__(self, beekeeper: Beekeeper, profile_name: str) -> None:
        assert beekeeper.is_running, "Encryption service can only be initialized after beekeeper is started."
        self._beekeeper = beekeeper
        self._profile_name = profile_name

    @staticmethod
    async def from_unlocked_beekeeper(beekeeper: Beekeeper) -> EncryptionService:
        profile_name = await GetUnlockedProfileName(beekeeper=beekeeper).execute_with_result()
        return EncryptionService(beekeeper, profile_name)

    @property
    def profile_name(self) -> str:
        return self._profile_name

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
