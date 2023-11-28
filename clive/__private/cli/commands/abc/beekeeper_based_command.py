from abc import ABC, abstractmethod
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.contextual_cli_command import ContextualCLICommand
from clive.__private.core.beekeeper import Beekeeper
from clive.core.url import Url


@dataclass(kw_only=True)
class BeekeeperCommon(ABC):
    beekeeper_remote: str | Url | None = None
    """If None, beekeeper will be launched locally."""

    @property
    @abstractmethod
    def beekeeper(self) -> Beekeeper:
        ...

    @property
    def beekeeper_remote_url(self) -> Url | None:
        if self.beekeeper_remote is None:
            return None
        if isinstance(self.beekeeper_remote, Url):
            return self.beekeeper_remote
        return Url.parse(self.beekeeper_remote)

    def _print_launching_beekeeper(self) -> None:
        message = (
            "Launching beekeeper..."
            if not self.beekeeper_remote_url
            else f"Using beekeeper at {self.beekeeper_remote_url}"
        )

        typer.echo(message)


@dataclass(kw_only=True)
class BeekeeperBasedCommand(ContextualCLICommand[Beekeeper], BeekeeperCommon, ABC):
    """A command that requires beekeeper to be running."""

    @property
    def beekeeper(self) -> Beekeeper:
        return self._context_manager_instance

    async def _create_context_manager_instance(self) -> Beekeeper:
        return Beekeeper(remote_endpoint=self.beekeeper_remote_url)

    async def run(self) -> None:
        await self.validate()
        self._skip_validation = True  # Skip validating again in the super().run()
        self._print_launching_beekeeper()
        await super().run()
