from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class DecryptWithProfileKey(CommandWithResult[str]):
    beekeeper: Beekeeper
    profile_name: str
    encrypted_content: str

    async def _execute(self) -> None:
        from clive.__private.core.encryption import encryption_wallet_name

        wallet_name = encryption_wallet_name(self.profile_name)
        get_public_keys_wrapper = await self.beekeeper.api.get_public_keys(wallet_name=wallet_name)
        assert len(get_public_keys_wrapper.keys) == 1, "Wallet with profile encryption key should contain one key."
        key_value = get_public_keys_wrapper.keys[0].public_key
        decrypt_wrapper = await self.beekeeper.api.decrypt_data(
            wallet_name=wallet_name,
            from_public_key=key_value,
            to_public_key=key_value,
            encrypted_content=self.encrypted_content,
        )
        self._result = decrypt_wrapper.decrypted_content
