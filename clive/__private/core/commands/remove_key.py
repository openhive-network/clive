from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.keys import PublicKey, PublicKeyAliased
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class RemoveKey(CommandInUnlocked, CommandPasswordSecured):
    beekeeper: Beekeeper
    wallet: str
    key_to_remove: PublicKey | PublicKeyAliased

    action_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.action_name = f"Removing a `{self.__get_key_description()}` key."

    async def _execute(self) -> None:
        public_key = self.key_to_remove.value
        await self.beekeeper.api.remove_key(wallet_name=self.wallet, password=self.password, public_key=public_key)

    def __get_key_description(self) -> str:
        if isinstance(self.key_to_remove, PublicKey):
            return self.key_to_remove.value
        if isinstance(self.key_to_remove, PublicKeyAliased):
            return self.key_to_remove.alias
        raise CliveError("Not implemented")
