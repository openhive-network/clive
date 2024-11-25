from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.exceptions import InvalidPasswordError

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.exceptions import WalletNotFoundError

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper, AsyncSession, AsyncWallet


@dataclass(kw_only=True)
class IsPasswordValid(CommandWithResult[bool]):
    """
    Check if the password is valid for the given wallet.

    Does it on the new session so the current session is not affected. E.g. unlock time remains the same.
    """

    beekeeper: AsyncBeekeeper
    wallet: str
    password: str

    async def _execute(self) -> None:
        async with await self.beekeeper.create_session() as session:
            wallet = await self._ensure_wallet_name_exists_and_open(session=session)
            self._result = await self._is_password_valid(wallet=wallet)

    async def _ensure_wallet_name_exists_and_open(self, session: AsyncSession) -> AsyncWallet:
        for wallet in await session.wallets_created:
            if wallet.name == self.wallet:
                return await session.open_wallet(name=self.wallet)
        raise WalletNotFoundError(self, self.wallet)

    async def _is_password_valid(self, wallet: AsyncWallet) -> bool:
        try:
            await wallet.unlock(password=self.password)
        except InvalidPasswordError:
            return False
        return True
