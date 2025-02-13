from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.decrypt_with_profile_key import DecryptWithProfileKey
from clive.__private.core.commands.encrypt_with_profile_key import EncryptWithProfileKey

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet


class EncryptionService:
    PROFILE_ENCRYPTION_WALLET_SUFFIX: Final[str] = "_profile_encryption"

    def __init__(self, wallet: AsyncUnlockedWallet) -> None:
        self._wallet = wallet

    @classmethod
    def get_encryption_wallet_name(cls, profile_name: str) -> str:
        return f"{profile_name}{cls.PROFILE_ENCRYPTION_WALLET_SUFFIX}"

    @classmethod
    def is_encryption_wallet_name(cls, wallet_name: str) -> bool:
        return wallet_name.endswith(cls.PROFILE_ENCRYPTION_WALLET_SUFFIX)

    async def decrypt(self, encrypted_content: str) -> str:
        return await DecryptWithProfileKey(
            unlocked_profile_encryption_wallet=self._wallet,
            encrypted_content=encrypted_content,
        ).execute_with_result()

    async def encrypt(self, content: str) -> str:
        return await EncryptWithProfileKey(
            unlocked_profile_encryption_wallet=self._wallet,
            content=content,
        ).execute_with_result()
