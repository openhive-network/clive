from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli


@dataclass(kw_only=True)
class ShowKeys(WorldBasedCommand):
    async def _run(self) -> None:
        profile_name = self.profile.name

        public_keys = list(self.profile.keys)
        print_cli(f"{profile_name}, your keys are:\n{public_keys}")
