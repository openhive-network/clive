from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import beekeepy as bk

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.encryption import EncryptionService

if TYPE_CHECKING:
    from beekeepy import AsyncSession


class MultipleProfilesUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Multiple profiles are unlocked on the beekeeper.")


class NoProfileUnlockedError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "There is no unlocked profile on the beekeeper.")


@dataclass(kw_only=True)
class GetUnlockedUserWallet(CommandWithResult[bk.AsyncUnlockedWallet]):
    """
    Get the unlocked user wallet - the one containing keys imported by user.

    Attributes:
        session: The session to use for fetching the unlocked wallet.
    """

    session: AsyncSession

    async def _execute(self) -> None:
        unlocked = [
            wallet
            for wallet in await self.session.wallets_unlocked
            if not EncryptionService.is_encryption_wallet_name(wallet.name)
        ]
        if len(unlocked) > 1:
            raise MultipleProfilesUnlockedError(self)
        if len(unlocked) < 1:
            raise NoProfileUnlockedError(self)
        self._result = unlocked[0]
