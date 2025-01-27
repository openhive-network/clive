from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from beekeepy import AsyncSession

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class CreateWallet(CommandWithResult[str]):
    app_state: AppState | None = None
    session: AsyncSession
    wallet_name: str
    password: str | None

    async def _execute(self) -> None:
        result = await self.session.create_wallet(name=self.wallet_name, password=self.password)
        if isinstance(result, tuple):
            unlocked_wallet, password = result
            self._result = password
        else:
            unlocked_wallet = result
            self._result = self.password

        if self.app_state:
            await self.app_state.unlock(unlocked_wallet)
