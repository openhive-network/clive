from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import MultipleProfilesUnlockedError, NoProfileUnlockedError
from clive.__private.core.constants.profile import PROFILE_ENCRYPTION_WALLET_SUFFIX

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper

WalletStatus: TypeAlias = Literal["all", "locked", "unlocked"]


@dataclass(kw_only=True)
class GetUnlockedProfileName(CommandWithResult[str]):
    beekeeper: Beekeeper

    async def _execute(self) -> None:
        wallets = (await self.beekeeper.api.list_wallets()).wallets
        unlocked = [wallet.name for wallet in wallets if wallet.unlocked]
        blockchain_keys = self._get_blockchain_keys_wallet_names(unlocked)
        profile_encryption = self._get_profile_encryption_wallet_names(unlocked)
        if len(blockchain_keys) < 1 or len(profile_encryption) < 1:
            raise NoProfileUnlockedError(self)
        if len(blockchain_keys) > 1 or len(profile_encryption) > 1:
            raise MultipleProfilesUnlockedError(self)
        self._result = blockchain_keys[0]

    def _is_profile_encryption_wallet(self, wallet_name: str) -> bool:
        return wallet_name.endswith(PROFILE_ENCRYPTION_WALLET_SUFFIX)

    def _get_blockchain_keys_wallet_names(self, wallet_names: list[str]) -> list[str]:
        return [name for name in wallet_names if not self._is_profile_encryption_wallet(name)]

    def _get_profile_encryption_wallet_names(self, wallet_names: list[str]) -> list[str]:
        return [name for name in wallet_names if self._is_profile_encryption_wallet(name)]
