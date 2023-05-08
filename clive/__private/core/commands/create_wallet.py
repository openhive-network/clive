from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command import Command

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperRemote
    from clive.__private.core.beekeeper.handle import BeekeeperLocal


@dataclass
class CreateWallet(Command[str]):
    beekeeper: BeekeeperLocal | BeekeeperRemote
    wallet: str
    password: str | None

    def execute(self) -> None:
        self._result = self.beekeeper.api.create(wallet_name=self.wallet, password=self.password).password
