from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.si.core.base import CommandBase

if TYPE_CHECKING:
    from clive.__private.core.world import World


class ProfileLoad(CommandBase[None]):
    def __init__(self, world: World) -> None:
        self.world = world

    async def _run(self) -> None:
        await self.world.load_profile_based_on_beekepeer()
