from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.exceptions import ProfileEncryptionKeyError
from clive.__private.core.constants.profile import ENCRYPTION_WALLET_TEMPLATE

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.beekeeper.model import BeekeeperPublicKeyType


@dataclass(kw_only=True)
class CommandProfileEncryption(Command, ABC):
    beekeeper: Beekeeper

    def get_wallet_name(self, profile_name: str) -> str:
        return ENCRYPTION_WALLET_TEMPLATE.format(profile_name)

    async def get_encryption_public_key(self, profile_name: str) -> BeekeeperPublicKeyType:
        keys = (await self.beekeeper.api.get_public_keys(wallet_name=self.get_wallet_name(profile_name))).keys
        if len(keys) != 1:
            raise ProfileEncryptionKeyError(self, len(keys))
        return keys[0]
