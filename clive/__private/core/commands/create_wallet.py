from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class CreateWallet(CommandWithResult[str]):
    app_state: AppState | None = None
    beekeeper: Beekeeper
    wallet: str
    password: str | None

    async def _execute(self) -> None:
        self._result = (await self.beekeeper.api.create(wallet_name=self.wallet, password=self.password)).password
        if self.app_state:
            self.app_state.activate()
