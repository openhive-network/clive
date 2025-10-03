from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import beekeepy as bk

from clive.__private.core.commands.abc.command_with_result import CommandWithResult

if TYPE_CHECKING:
    from beekeepy import AsyncSession


@dataclass(kw_only=True)
class CreateUserWallet(CommandWithResult[bk.AsyncUnlockedWallet]):
    session: AsyncSession
    profile_name: str
    password: str

    async def _execute(self) -> None:
        self._result = await self.session.create_wallet(name=self.profile_name, password=self.password)
