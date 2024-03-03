from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from helpy.exceptions import RequestError

from clive.__private.core.commands.abc.command import CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from clive.models.aliased import Session


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

    session: Session
    wallet: str
    password: str

    async def _execute(self) -> None:
        wallet = await self.session.open_wallet(name=self.wallet)
        try:
            await wallet.unlock(password=self.password)
        except RequestError:
            self._result = False
        else:
            self._result = True
