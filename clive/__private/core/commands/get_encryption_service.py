from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.get_unlocked_encryption_wallet import GetUnlockedEncryptionWallet
from clive.__private.core.commands.get_unlocked_user_wallet import GetUnlockedUserWallet
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.wallet_container import WalletContainer

if TYPE_CHECKING:
    from beekeepy import AsyncSession


@dataclass(kw_only=True)
class GetEncryptionService(CommandWithResult[EncryptionService]):
    """Get the encryption service - created from unlocked user wallet and unlocked encryption wallet."""

    session: AsyncSession

    async def _execute(self) -> None:
        user_wallet = await GetUnlockedUserWallet(session=self.session).execute_with_result()
        encryption_wallet = await GetUnlockedEncryptionWallet(session=self.session).execute_with_result()
        self._result = EncryptionService(WalletContainer(user_wallet, encryption_wallet))
