from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.models.aliased import Session, UnlockedWallet

if TYPE_CHECKING:

    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class CreateWallet(CommandWithResult[UnlockedWallet]):
    app_state: AppState | None = None
    session: Session
    wallet: str
    password: str

    async def _execute(self) -> None:
        self._result = await self.session.create_wallet(name=self.wallet, password=self.password)
        if self.app_state:
            self.app_state.activate()
