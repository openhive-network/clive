from abc import ABC, abstractmethod
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.core.beekeeper import Beekeeper
from clive.core.url import Url


@dataclass(kw_only=True)
class BeekeeperBasedCommand(ExternalCLICommand, ABC):
    """A command that requires beekeeper to be running."""

    beekeeper_remote: str | Url | None
    """If None, beekeeper will be launched locally."""

    _beekeeper: Beekeeper | None = None

    @property
    def beekeeper(self) -> Beekeeper:
        assert self._beekeeper is not None, "Beekeeper should be set before running the command."
        return self._beekeeper

    @property
    def beekeeper_remote_url(self) -> Url | None:
        if self.beekeeper_remote is None:
            return None
        if isinstance(self.beekeeper_remote, Url):
            return self.beekeeper_remote
        return Url.parse(self.beekeeper_remote)

    @abstractmethod
    async def _run(self) -> None:
        """The actual implementation of the command."""

    async def run(self) -> None:
        self._print_launching_beekeeper()

        async with Beekeeper(remote_endpoint=self.beekeeper_remote_url) as beekeeper:
            self._beekeeper = beekeeper
            await self._run()

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)
