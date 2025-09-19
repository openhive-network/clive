from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.beekeeper_manager import AsyncUnlockedWallet
from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from beekeepy import AsyncSession


@dataclass(kw_only=True)
class CreateUserWallet(CommandWithResult[AsyncUnlockedWallet]):
    session: AsyncSession
    profile_name: str
    password: str

    async def _execute(self) -> None:
        self._result = await self.session.create_wallet(name=self.profile_name, password=self.password)
