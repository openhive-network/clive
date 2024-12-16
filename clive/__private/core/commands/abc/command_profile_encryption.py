from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.exceptions import ProfileEncryptionKeyError

if TYPE_CHECKING:
    from beekeepy import AsyncUnlockedWallet

    from clive.__private.models.schemas import PublicKey


@dataclass(kw_only=True)
class CommandProfileEncryption(Command, ABC):
    """A command that requires profile encryption wallet unlocked."""

    unlocked_profile_encryption_wallet: AsyncUnlockedWallet

    @property
    def encryption_wallet_name(self) -> str:
        return self.unlocked_profile_encryption_wallet.name

    @property
    async def encryption_public_key(self) -> PublicKey:
        keys = await self.unlocked_profile_encryption_wallet.public_keys
        if len(keys) != 1:
            raise ProfileEncryptionKeyError(self, len(keys))
        return keys[0]
