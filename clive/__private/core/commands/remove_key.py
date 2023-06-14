from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.command_secured import CommandSecured
from clive.__private.storage.mock_database import PublicKey, PublicKeyAliased
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


@dataclass(kw_only=True)
class RemoveKey(CommandSecured[None]):
    beekeeper: Beekeeper
    wallet: str
    key_to_remove: PublicKey | PublicKeyAliased

    def __post_init__(self) -> None:
        self.action_name = f"Removing a `{self.__get_key_description()}` key."

    def _execute(self) -> None:
        public_key = self.key_to_remove.value
        self.beekeeper.api.remove_key(wallet_name=self.wallet, password=self._password, public_key=public_key)

    def __get_key_description(self) -> str:
        if isinstance(self.key_to_remove, PublicKey):
            return self.key_to_remove.value
        if isinstance(self.key_to_remove, PublicKeyAliased):
            return self.key_to_remove.alias
        raise CliveError("Not implemented")
