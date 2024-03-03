from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.app_state import AppState
from clive.__private.core.commands.abc.command_in_active import CommandInActive
from clive.__private.core.commands.abc.command_secured import CommandPasswordSecured
from clive.__private.core.commands.activate import Activate
from clive.__private.core.keys import PublicKey, PublicKeyAliased
from clive.exceptions import CliveError
from schemas.fields.basic import PublicKey as SchemasPublicKey

if TYPE_CHECKING:
    from clive.models.aliased import Session, Wallet


@dataclass(kw_only=True)
class RemoveKey(CommandInActive, CommandPasswordSecured):
    session: Session
    wallet: Wallet
    key_to_remove: PublicKey | PublicKeyAliased

    action_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.action_name = f"Removing a `{self.__get_key_description()}` key."

    async def _execute(self) -> None:
        if self.wallet.unlocked is None:
            assert isinstance(self.app_state, AppState)
            Activate(password=self.password, app_state=self.app_state, wallet=self.wallet.name, session=self.session)
            self.wallet = self.wallet.unlocked
        unlocked = await self.wallet.unlocked
        assert unlocked is not None
        public_key = self.key_to_remove.value
        await unlocked.remove_key(confirmation_password=self.password, key=SchemasPublicKey(public_key))

    def __get_key_description(self) -> str:
        if isinstance(self.key_to_remove, PublicKey):
            return self.key_to_remove.value
        if isinstance(self.key_to_remove, PublicKeyAliased):
            return self.key_to_remove.alias
        raise CliveError("Not implemented")
