from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.py.base import UnlockedClivePy


class ConfigureInterface:
    """Interface for profile configuration actions (create/load)."""

    def __init__(self, clive_instance: UnlockedClivePy) -> None:
        self.clive = clive_instance

    async def profile_load(self) -> None:
        """
        Reload the currently unlocked profile from storage.

        This method is rarely needed as PyWorld automatically loads the unlocked profile during setup.
        Use this only if you need to refresh the profile state after external changes.
        """
        await self.clive._world.load_profile_based_on_beekepeer()
