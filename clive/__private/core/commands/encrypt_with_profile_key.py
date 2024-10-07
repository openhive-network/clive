from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.profile import encryption_wallet_name

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class EncryptWithProfileKey(CommandWithResult[str]):
    beekeeper: Beekeeper
    profile_name: str
    content: str

    async def _execute(self) -> None:
        wallet_name = encryption_wallet_name(self.profile_name)
        get_public_keys_wrapper = await self.beekeeper.api.get_public_keys(wallet_name=wallet_name)
        assert len(get_public_keys_wrapper.keys) == 1, "Wallet with profile encryption key should contain one key."
        key_value = get_public_keys_wrapper.keys[0].public_key
        wrapper = await self.beekeeper.api.encrypt_data(
            wallet_name=wallet_name,
            from_public_key=key_value,
            to_public_key=key_value,
            content=self.content,
        )
        self._result = wrapper.encrypted_content
