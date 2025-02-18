from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.decrypt import Decrypt
from clive.__private.core.commands.encrypt import Encrypt

if TYPE_CHECKING:
    from clive.__private.core.wallet_container import WalletContainer


class EncryptionService:
    _ENCRYPTION_KEY_WALLET_NAME_SUFFIX: Final[str] = "_encryption"

    def __init__(self, wallets: WalletContainer) -> None:
        self._wallets = wallets

    @classmethod
    def get_encryption_wallet_name(cls, profile_name: str) -> str:
        return f"{profile_name}{cls._ENCRYPTION_KEY_WALLET_NAME_SUFFIX}"

    @classmethod
    def is_encryption_wallet_name(cls, wallet_name: str) -> bool:
        return wallet_name.endswith(cls._ENCRYPTION_KEY_WALLET_NAME_SUFFIX)

    async def decrypt(self, encrypted_content: str) -> str:
        return await Decrypt(
            unlocked_wallet=self._wallets.user_wallet,
            unlocked_encryption_wallet=self._wallets.encryption_wallet,
            encrypted_content=encrypted_content,
        ).execute_with_result()

    async def encrypt(self, content: str) -> str:
        return await Encrypt(
            unlocked_wallet=self._wallets.user_wallet,
            unlocked_encryption_wallet=self._wallets.encryption_wallet,
            content=content,
        ).execute_with_result()
