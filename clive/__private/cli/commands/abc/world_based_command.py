from abc import ABC
from dataclasses import dataclass

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.world import TyperWorld, World
from clive.core.url import Url


@dataclass(kw_only=True)
class WorldBasedCommand(BeekeeperBasedCommand, ABC):
    """A command that requires a world."""

    profile_name: str
    use_beekeeper: bool = True
    beekeeper_remote: str | Url | None = None
    """If None, beekeeper will be launched locally when also use_beekeeper is set."""

    _world: World | None = None

    @property
    def world(self) -> World:
        assert self._world is not None, "World should be set before running the command."
        return self._world

    @property
    def beekeeper(self) -> Beekeeper:
        return self.world.beekeeper

    async def run(self) -> None:
        if self.use_beekeeper:
            self._print_launching_beekeeper()

        async with TyperWorld(
            profile_name=self.profile_name,
            use_beekeeper=self.use_beekeeper,
            beekeeper_remote_endpoint=self.beekeeper_remote_url,
        ) as world:
            self._world = world
            await self._run()
