from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.profile import Profile, encryption_key_alias, encryption_wallet_name

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class CreateProfileEncryptionWallet(CommandWithResult[str]):
    beekeeper: Beekeeper
    profile: Profile
    password: str | None

    async def _execute(self) -> None:
        wallet_name = encryption_wallet_name(self.profile.name)
        self._result = (await self.beekeeper.api.create(wallet_name=wallet_name, password=self.password)).password
        alias = encryption_key_alias(self.profile.name)
        private_key = iwax.generate_private_key()
        private_key_aliased = private_key.with_alias(alias)
        await self.beekeeper.api.import_key(wallet_name=wallet_name, wif_key=private_key_aliased.value)
        self.profile.set_encryption_key(private_key_aliased.calculate_public_key())
