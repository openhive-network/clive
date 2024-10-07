from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.profile import Profile, encryption_wallet_name

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class EncryptWithProfileKey(CommandWithResult[str]):
    beekeeper: Beekeeper
    profile: Profile
    content: str

    async def _execute(self) -> None:
        wallet_name = encryption_wallet_name(self.profile.name)
        key = self.profile.encryption_key
        wrapper = await self.beekeeper.api.encrypt_data(
            wallet_name=wallet_name,
            from_public_key=key.value,
            to_public_key=key.value,
            content=self.content,
        )
        self._result = wrapper.encrypted_content
