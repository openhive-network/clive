from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class BeekeeperInfo(WorldBasedCommand):
    @property
    def should_require_unlocked_wallet(self) -> bool:
        return False

    async def _run(self) -> None:
        session = await self.world.beekeeper_manager.beekeeper.session
        info = (await session.get_info()).json(order="sorted")
        print_cli(info)
