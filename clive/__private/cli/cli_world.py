from __future__ import annotations

from typing import cast, override

from clive.__private.core.commands.commands import CLICommands
from clive.__private.core.commands.get_unlocked_user_wallet import NoProfileUnlockedError
from clive.__private.core.world import World


class CLIWorld(World):
    @property
    def commands(self) -> CLICommands:
        return cast("CLICommands", super().commands)

    @override
    async def _setup(self) -> None:
        await super()._setup()
        try:
            await self.load_profile_based_on_beekepeer()
        except NoProfileUnlockedError:
            await self.switch_profile(None)

    def _setup_commands(self) -> CLICommands:
        return CLICommands(self)
