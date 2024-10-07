from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import MultipleWalletsUnlockedError, ProfileNotUnlockedError
from clive.__private.core.constants.profile import PROFILE_ENCRYPTION_WALLET_SUFFIX

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class GetUnlockedProfileName(CommandWithResult[str]):
    beekeeper: Beekeeper

    async def _execute(self) -> None:
        wallets = (await self.beekeeper.api.list_wallets()).wallets
        unlocked_names = [wallet.name for wallet in wallets if wallet.unlocked]
        profile_encryption_wallet_names = [
            name for name in unlocked_names if name.endswith(PROFILE_ENCRYPTION_WALLET_SUFFIX)
        ]
        blockchain_key_wallet_names = [
            name for name in unlocked_names if not name.endswith(PROFILE_ENCRYPTION_WALLET_SUFFIX)
        ]
        if len(profile_encryption_wallet_names) == 0 and len(blockchain_key_wallet_names) == 0:
            raise ProfileNotUnlockedError(self)
        if len(profile_encryption_wallet_names) != 1 or len(blockchain_key_wallet_names) != 1:
            raise MultipleWalletsUnlockedError(self)
        self._result = blockchain_key_wallet_names[0]
