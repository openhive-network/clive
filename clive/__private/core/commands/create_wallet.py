from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from beekeepy import AsyncSession

    from clive import World
    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class CreateWallet(CommandWithResult[str]):
    app_state: AppState | None = None
    session: AsyncSession
    wallet_name: str
    password: str | None
    world: World | None = None
    """If specified, this command will set newly created wallet to given world"""

    async def _execute(self) -> None:
        result = await self.session.create_wallet(name=self.wallet_name, password=self.password)
        if isinstance(result, tuple):
            self._result = result[1]
            if self.world is not None:
                await self.world.set_wallet(result[0])
        else:
            self._result = self.password
            if self.world is not None:
                await self.world.set_wallet(result)

        if self.app_state:
            self.app_state.unlock()
