from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper


@dataclass(kw_only=True)
class CreateWallet(Command[str]):
    beekeeper: Beekeeper
    wallet: str
    password: str | None

    def _execute(self) -> None:
        self._result = self.beekeeper.api.create(wallet_name=self.wallet, password=self.password).password
