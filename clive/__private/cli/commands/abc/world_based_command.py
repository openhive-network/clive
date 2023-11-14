from abc import ABC
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.world import TyperWorld, World
from clive.core.url import Url


@dataclass(kw_only=True)
class WorldBasedCommand(ExternalCLICommand, ABC):
    """A command that requires a world."""

    profile_name: str
    use_beekeeper: bool = True
    beekeeper_remote: str | Url | None
    """If None, beekeeper will be launched locally when also use_beekeeper is set."""

    _world: World | None = None

    @property
    def world(self) -> World:
        assert self._world is not None, "World should be set before running the command."
        return self._world

    @property
    def beekeeper_remote_url(self) -> Url | None:
        if self.beekeeper_remote is None:
            return None
        if isinstance(self.beekeeper_remote, Url):
            return self.beekeeper_remote
        return Url.parse(self.beekeeper_remote)

    async def _run(self) -> None:
        """The actual implementation of the command."""

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

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)
