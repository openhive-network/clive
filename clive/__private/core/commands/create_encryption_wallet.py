from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import beekeepy as bk

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.keys import PrivateKey

if TYPE_CHECKING:
    from beekeepy import AsyncSession


@dataclass(kw_only=True)
class CreateEncryptionWallet(CommandWithResult[bk.AsyncUnlockedWallet]):
    session: AsyncSession
    profile_name: str
    password: str

    async def _execute(self) -> None:
        unlocked_encryption_wallet = await self.session.create_wallet(
            name=EncryptionService.get_encryption_wallet_name(self.profile_name), password=self.password
        )
        await unlocked_encryption_wallet.import_key(
            private_key=PrivateKey.create_from_seed(self.password, account_name=self.profile_name).value
        )
        self._result = unlocked_encryption_wallet
