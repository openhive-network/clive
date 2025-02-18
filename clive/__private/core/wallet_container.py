from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet


@dataclass(kw_only=True)
class WalletContainer:
    user_wallet: AsyncUnlockedWallet
    encryption_wallet: AsyncUnlockedWallet

    def __post_init__(self) -> None:
        encryption_wallet_name = EncryptionService.get_encryption_wallet_name(self.user_wallet.name)
        message = (
            f"wallet name {self.user_wallet.name} should match encryption wallet name {self.encryption_wallet.name}"
        )
        assert encryption_wallet_name == self.encryption_wallet.name, message

    @property
    def name(self) -> str:
        return self.user_wallet.name
