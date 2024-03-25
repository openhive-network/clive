from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


class IsPasswordValidCommandError(CommandError):
    pass


class WalletNotFoundError(IsPasswordValidCommandError):
    def __init__(self, command: IsPasswordValid, wallet_name: str):
        super().__init__(command, f"Wallet `{wallet_name}` not found on the beekeeper.")


@dataclass(kw_only=True)
class IsPasswordValid(CommandWithResult[bool]):
    """
    Check if the password is valid for the given wallet.

    Does it on the new session so the current session is not affected. E.g. unlock time remains the same.
    """

    beekeeper: Beekeeper
    wallet: str
    password: str

    async def _execute(self) -> None:
        new_session_token = (await self.beekeeper.api.create_session()).token

        await self._ensure_wallet_name_exists(token=new_session_token)

        result = await self._is_password_valid(token=new_session_token)
        await self.beekeeper.api.close_session(token=new_session_token)
        self._result = result

    async def _ensure_wallet_name_exists(self, token: str) -> None:
        stored_wallets = (await self.beekeeper.api.list_created_wallets(token=token)).wallets  # type: ignore[call-arg]
        stored_wallet_names = [wallet.name for wallet in stored_wallets]

        if self.wallet not in stored_wallet_names:
            await self.beekeeper.api.close_session(token=token)
            raise WalletNotFoundError(self, self.wallet)

    async def _is_password_valid(self, token: str) -> bool:
        try:
            await self.beekeeper.api.unlock(wallet_name=self.wallet, password=self.password, token=token)  # type: ignore[call-arg]
        except CommunicationError:
            return False
        return True
