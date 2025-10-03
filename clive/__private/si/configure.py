from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.si.core.configure import ProfileLoad

if TYPE_CHECKING:
    from clive.__private.si.base import ProfileBase


class ConfigureInterface:
    """Interface for profile configuration actions (create/load)."""

    def __init__(self, clive_instance: ProfileBase) -> None:
        self.clive = clive_instance

    async def profile_load(self) -> None:
        """Load an existing profile."""
        await ProfileLoad(self.clive.world).run()
