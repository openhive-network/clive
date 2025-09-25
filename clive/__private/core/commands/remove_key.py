from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKey


@dataclass(kw_only=True)
class RemoveKey(CommandInUnlocked):
    """
    Remove a private key that has been previously imported into the beekeeper wallet.

    Attributes:
        key_to_remove: The public key corresponding to the private key that is about to be removed.
    """

    key_to_remove: PublicKey

    async def _execute(self) -> None:
        public_key = self.key_to_remove.value
        await self.unlocked_wallet.remove_key(key=public_key)
