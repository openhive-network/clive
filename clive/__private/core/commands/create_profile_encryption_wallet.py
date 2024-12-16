from __future__ import annotations

from dataclasses import dataclass

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command_profile_encryption import CommandProfileEncryption
from clive.__private.core.commands.abc.command_with_result import CommandWithResult


@dataclass(kw_only=True)
class CreateProfileEncryptionWallet(CommandProfileEncryption, CommandWithResult[str]):
    profile_name: str
    password: str | None

    def generate_wif_key(self) -> str:
        private_key = iwax.generate_private_key()
        return private_key.value

    async def _execute(self) -> None:
        wallet_name = self.get_wallet_name(profile_name=self.profile_name)
        self._result = (await self.beekeeper.api.create(wallet_name=wallet_name, password=self.password)).password
        await self.beekeeper.api.import_key(wallet_name=wallet_name, wif_key=self.generate_wif_key())
