from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet


@dataclass(kw_only=True)
class WalletContainer:
    blockchain_keys: AsyncUnlockedWallet
    profile_encryption: AsyncUnlockedWallet

    def __post_init__(self) -> None:
        encryption_wallet_name = EncryptionService.get_encryption_wallet_name(self.blockchain_keys.name)
        message = (
            f"wallet name {self.blockchain_keys.name} should match"
            f" encryption wallet name {self.profile_encryption.name}"
        )
        assert encryption_wallet_name == self.profile_encryption.name, message

    @property
    def name(self) -> str:
        return self.blockchain_keys.name
