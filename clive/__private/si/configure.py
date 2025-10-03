from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.si.base import ProfileBase
from clive.__private.si.core.configure import ProfileCreate, ProfileLoad


class ConfigureInterface:
    """Interface for profile configuration actions (create/load)."""

    def __init__(self, clive_instance: ProfileBase) -> None:
        self.clive = clive_instance

    async def profile_create(self, profile_name: str, password: str) -> None:
        """Create a new profile."""
        await ProfileCreate(self.clive.world, profile_name, password).run()

    async def profile_load(self) -> None:
        """Load an existing profile."""
        await ProfileLoad(self.clive.world).run()
